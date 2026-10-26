from __future__ import annotations
import argparse
from pathlib import Path
from openpyxl import Workbook

HEADERS = ["Num", "Date", "KOL Name", "Platform", "Handle", "Profile URL", "Email", "Country", "Followers", "Avg Views", "Best Video Views", "Contact Status", "Cooperation Type", "Quote", "Internal Rating", "Next Follow-up Date"]

def main():
    parser = argparse.ArgumentParser(description="Create a blank KOL tracker. Existing files are preserved.")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs" / "varla_kol_tracker.xlsx")
    target = parser.parse_args().output
    if target.exists():
        print("Already exists; no change:", target)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    book = Workbook()
    sheet = book.active
    sheet.title = "KOL建联台账"
    sheet.append(HEADERS)
    sheet.freeze_panes = "A2"
    book.save(target)
    print("Created blank tracker:", target)

if __name__ == "__main__":
    main()
