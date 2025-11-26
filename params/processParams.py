import os
import sys
import logging
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
from parser import parse_sheet_to_json, isSheetValid

LOG_FILE = "sheet_validation.log"

def init_logger():
    logging.basicConfig(
        filename=LOG_FILE,
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s",
        level=logging.INFO
    )

def ensure_output_dir(base_dir: Path) -> Path:  #check if output dir exists and create it
    out_dir = base_dir / "jsonParams"
    out_dir.mkdir(exist_ok=True)
    return out_dir

def scan_for_xlsx(input_dir: Path):     #get excels in input dir
    return list(input_dir.glob("*.xlsx"))

def safe_load_excel(path: Path):
    try:
        return pd.ExcelFile(path)
    except Exception as e:
        print(f"[ERROR] Could not load {path.name}: {e}")
        return None

def process_workbook(excel_path: Path, out_dir: Path):
    excel = safe_load_excel(excel_path)
    if excel is None:
        return

    print(f"\n[INFO] Processing {excel_path.name}")

    for idx, sheet in enumerate(excel.sheet_names):
        print(f"  → Checking sheet: {sheet}")

        try:
            df = excel.parse(sheet)
        except Exception as e:
            print(f"    [SKIP] Could not read sheet '{sheet}': {e}")
            logging.warning(
                    f"Reading failed | File: '{excel_path}' | Sheet: '{sheet}'"
                )
            continue

        if df.empty:
            print(f"    [SKIP] Sheet '{sheet}' is empty.")
            logging.warning(
                    f"Empty Sheet | File: '{excel_path}' | Sheet: '{sheet}'"
                )
            continue

        try:
            if not isSheetValid(df):    # checks if this sheet matches customer hand-off sheet
                print(f"    [SKIP] Sheet '{sheet}' failed validation.")
                logging.warning(
                    f"Validation failed | File: '{excel_path}' | Sheet: '{sheet}'"
                )
                continue
        except Exception as e:
            print(f"    [WARN] Validation error on '{sheet}': {e}")
            logging.error(
                f"Validation exception | File: '{excel_path}' | Sheet: '{sheet}' | Error: {e}"
            )
            continue

        # Build output JSON filename
        out_file = out_dir / f"{excel_path.stem}_{str(sheet).replace(' ', '_')}.json"

        # PARSE
        try:
            parse_sheet_to_json(
                excel_file=str(excel_path),
                output_file=str(out_file),
                sheet_name=sheet,  # sheet can be name or index
            )
            print(f"    [OK] Wrote {out_file.name}")
        except Exception as e:
            print(f"    [ERROR] parse_sheet_to_json failed for '{sheet}': {e}")
            logging.warning(
                    f"Parse failed | File: '{excel_path}' | Sheet: '{sheet}'"
                )

def process_directory(source_dir: str):
    """Scan directory and process all xlsx files."""
    init_logger()
    base = Path(source_dir).resolve()
    out_dir = ensure_output_dir(base)   #this places the output dir inside of the source dir, but could find better place

    xlsx_files = scan_for_xlsx(base)
    if not xlsx_files:
        print(f"[INFO] No .xlsx files found in {base}")
        return

    for file in xlsx_files:
        process_workbook(file, out_dir)


#Use CLI args to pass dir names 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage:\n   python processParams.py <directory_with_excel_files>\n")
        sys.exit(1)

    process_directory(sys.argv[1])
