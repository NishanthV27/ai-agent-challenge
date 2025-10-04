# ai-agent-challenge
Coding agent challenge which write custom parsers for Bank statement PDF.

# Agent-as-Coder: Bank Statement Parser AI Agent

## Project Goal
This AI agent automatically creates custom parsers for bank statements (PDFs), extracts transactions (Date, Description, Amount, Balance), compares the output to a reference CSV, and retries parsing up to 3 times if the first attempts fail. It works for any bank (ICICI, SBI, HDFC) without manual code edits.

## How to Run
To use the agent, first **clone the repository** with `git clone https://github.com/Nishanthv27/ai-agent-challenge.git` and navigate into the folder. Then, **create and activate a virtual environment** using `python -m venv venv` and `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows). Next, **install dependencies** via `pip install -r requirements.txt`. Prepare your **data folder** by placing the PDF bank statement and `result.csv` inside, e.g., `data/icici/`. Finally, **run the AI agent** with `python agent.py --target icici --data data/icici`; the agent will automatically generate a parser if missing, extract transactions, compare with the reference CSV, retry up to 3 times if needed, and print all extracted transactions with summary statistics.

## Agent Workflow
The AI agent first checks whether a parser exists for the target bank and creates one automatically if missing. It then loads the parser, extracts transactions from the PDF into a DataFrame, and compares the results with the reference CSV. If there are mismatches, it retries parsing up to three times using progressively relaxed rules to ensure self-correction. Once successful, it prints all extracted transactions along with summary statistics including total transactions, sum of amounts, and final balance, completing the parsing process autonomously.
┌───────────────────────────┐
│ Start / CLI input          │
│ python agent.py --target   │
│ icici --data data/icici    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Check if parser exists     │
│ (custom_parsers/{bank})   │
└─────────────┬─────────────┘
              │
        No    │    Yes
 ┌────────────▼───────────┐
 │ Create parser template  │
 │ (auto-generate code)    │
 └────────────┬───────────┘
              │
              ▼
┌───────────────────────────┐
│ Load parser dynamically    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Loop attempts 1 → 3       │
│ - Attempt 1: strict regex │
│ - Attempt 2: relaxed regex│
│ - Attempt 3: split lines  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Parse PDF → DataFrame     │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Compare with CSV           │
│ DataFrame.equals()        │
└───────┬───────────────────┘
        │
  Match │ No match
        ▼
┌───────────────────────────┐
│ SUCCESS: Stop             │
└───────────────────────────┘
        │
┌───────────────────────────┐
│ WARNING: Retry next attempt│
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│ FAIL after 3 attempts      │
└───────────────────────────┘
