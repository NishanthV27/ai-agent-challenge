import pandas as pd
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
                   
                    if attempt == 1:
                        match = re.match(r"(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})", line)
                   
                    elif attempt == 2:
                        match = re.match(r"(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d,]+\.\d{2})\s*([\d,]+\.\d{2})", line)
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
