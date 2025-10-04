

import argparse
import importlib
import sys
from pathlib import Path
import pandas as pd
import re
import pdfplumber

TEMPLATE = '''import pandas as pd
import re
import pdfplumber

class Parser:
    def parse(self, pdf_path: str, attempt: int = 1) -> pd.DataFrame:
        transactions = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.splitlines():
                    # attempt 1: strict regex
                    if attempt == 1:
                        match = re.match(r"(\\d{{2}}-\\d{{2}}-\\d{{4}})\\s+(.*?)\\s+([\\d,]+\\.\\d{{2}})\\s+([\\d,]+\\.\\d{{2}})", line)
                    # attempt 2: relaxed regex
                    elif attempt == 2:
                        match = re.match(r"(\\d{{2}}-\\d{{2}}-\\d{{4}})\\s+(.+?)\\s+([\\d,]+\\.\\d{{2}})\\s*([\\d,]+\\.\\d{{2}})", line)
                    # attempt 3: split line into 4 parts if regex fails
                    else:
                        parts = line.split()
                        if len(parts) >= 4:
                            match = parts[:4]
                        else:
                            match = None
                    if match:
                        if isinstance(match, list):
                            transactions.append([match[0], match[1], float(match[2].replace(',', '')), float(match[3].replace(',', ''))])
                        else:
                            date, desc, amt, bal = match.groups()
                            transactions.append([date, desc.strip(), float(amt.replace(',', '')), float(bal.replace(',', ''))])
        df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount", "Balance"])
        return df
'''

def ensure_parser(bank: str):
    """Automatically create parser template if missing"""
    parser_folder = Path("custom_parsers")
    parser_folder.mkdir(exist_ok=True)
    parser_file = parser_folder / f"{bank}_parser.py"
    if not parser_file.exists():
        print(f"[AGENT] Parser for '{bank}' not found. Creating automatically...")
        parser_file.write_text(TEMPLATE)
        print(f"[AGENT] Created parser: {parser_file}")
    return parser_file

def load_parser(bank: str):
    module = importlib.import_module(f"custom_parsers.{bank}_parser")
    parser_class = getattr(module, "Parser", None)
    if parser_class is None:
        raise ValueError(f"Parser class missing in {bank}_parser")
    return parser_class()

def test_parser(df: pd.DataFrame, csv_file: Path) -> bool:
    expected = pd.read_csv(csv_file)
    try:
        
        df_cmp = df.copy()
        df_cmp["Amount"] = df_cmp["Amount"].astype(float)
        df_cmp["Balance"] = df_cmp["Balance"].astype(float)
        expected["Amount"] = expected["Amount"].astype(float)
        expected["Balance"] = expected["Balance"].astype(float)
        return df_cmp.equals(expected)
    except Exception as e:
        print(f"[TEST ERROR] {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Bank name (e.g., icici, sbi)")
    parser.add_argument("--data", required=True, help="Path to bank data folder")
    args = parser.parse_args()

    bank = args.target.lower()
    data_dir = Path(args.data)

    pdf_file = next(data_dir.glob("*.pdf"), None)
    csv_file = data_dir / "result.csv"

    if not pdf_file or not csv_file.exists():
        print(f"[ERROR] PDF or CSV missing in {data_dir}")
        sys.exit(1)

    ensure_parser(bank)
    parser_instance = load_parser(bank)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"\n[AGENT] Attempt {attempt} parsing...")
        df = parser_instance.parse(str(pdf_file), attempt=attempt)

        
        df.to_csv(csv_file, index=False)

       
        print("[OUTPUT ALL] Full extracted data:")
        print(df.to_string())

        print(f"\nTotal transactions extracted: {len(df)}")
        print(f"Total amount sum: {df['Amount'].sum():.2f}")
        print(f"Final balance (last row): {df['Balance'].iloc[-1]:.2f}")

        if test_parser(df, csv_file):
            print(f"[SUCCESS] Parser output matches CSV ✅")
            break
        else:
            print(f"[WARNING] Parser output does not match CSV, attempt {attempt}/{max_attempts}")
            if attempt == max_attempts:
                print(f"[FAIL] Parser failed after {max_attempts} attempts ❌")
                sys.exit(1)

if __name__ == "__main__":
    main()
