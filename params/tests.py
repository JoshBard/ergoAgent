import unittest
from rapidfuzz import fuzz # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from parser import parseSize, normCols, cleanTextCol, loadJson, writeJson, fuzzyMap, parse_date_to_yyyymmdd, isValid, parse_sheet_to_json
import json
import os

#CONFIG
EXCEL_FILE = "exampleParameters.xlsx"
SCHEMA = "parameters.json"
OUTPUT_FILE = "testout.json"
DICTIONARY = "mapping.json"

print("Testing Suite")

class TestParser(unittest.TestCase):

    def test_parse_size_valid(self):
        self.assertEqual(parseSize("10X12"), [10.0, 12.0])
        self.assertEqual(parseSize('30" x 60"'), [30.0, 60.0])
        self.assertEqual(parseSize('10"2\'x 10"2\''), [122.0, 122.0])
        self.assertEqual(parseSize("10 ft 2 in x 12 ft 6 in"), [122.0, 150.0])
    
    def test_parse_size_invalid(self):
        self.assertEqual(parseSize("unknown"), [-1, -1])
        self.assertEqual(parseSize(""), [-1, -1])
        self.assertEqual(parseSize(None), [-1, -1])
        self.assertEqual(parseSize("67 67 67 67 67"), [-1,-1])

    def test_iso_format(self):
        self.assertEqual(parse_date_to_yyyymmdd("2025-11-21"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("2025/11/21"), "20251121")

    def test_american_format(self):
        self.assertEqual(parse_date_to_yyyymmdd("11/21/2025"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("Nov 21, 2025"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("November 21 2025"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("11-21-2025"), "20251121")

    def test_european_format(self):
        self.assertEqual(parse_date_to_yyyymmdd("21/11/2025", day_first=True), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("21-11-2025", day_first=True), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("21 Nov 2025", day_first=True), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("21 November 2025", day_first=True), "20251121")

    def test_day_first_auto_detection(self):
        # first > 12 → day-first
        self.assertEqual(parse_date_to_yyyymmdd("21/03/2025"), "20250321")
        # second > 12 → month-first
        self.assertEqual(parse_date_to_yyyymmdd("03/21/2025"), "20250321")

    def test_invalid_input(self):
        self.assertEqual(parse_date_to_yyyymmdd(""), "")
        self.assertEqual(parse_date_to_yyyymmdd(None), "")
        self.assertEqual(parse_date_to_yyyymmdd("not a date"), "")

    def test_with_ordinals(self):
        self.assertEqual(parse_date_to_yyyymmdd("21st Nov 2025"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("Nov 21st 2025"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("1st Jan 2025"), "20250101")

    def test_with_extra_text(self):
        self.assertEqual(parse_date_to_yyyymmdd("on 21/11/2025 we start"), "20251121")
        self.assertEqual(parse_date_to_yyyymmdd("Deadline: Nov 21, 2025"), "20251121")

    def test_read_excel(self):
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        self.assertEqual(len(df.columns), 8)

    def test_normCols(self):
        df = pd.DataFrame(columns=[" Column A ", "Column B", "c o l"])
        df2 = normCols(df)
        self.assertEqual(df2.columns.tolist(), ["COLUMN_A", "COLUMN_B", "C_O_L"])

    def test_cleanTextCol(self):
        df = pd.DataFrame({
            "name": ["  alice ", "Bob  "],
            "age": [25, 30]
        })

        df2 = cleanTextCol(df, ["name", "age"])
        self.assertEqual(df2["name"].tolist(), ["ALICE", "BOB"])
        self.assertEqual(df2["age"].tolist(), ["25", "30"])

    def test_loadJson(self):
        test_file = "test_temp.json"
        expected = {"a": 1, "b": 2}

        with open(test_file, "w") as f:
            json.dump(expected, f)

        result = loadJson(test_file)
        os.remove(test_file)
        self.assertEqual(result, expected)

    # def test_writeJson(self):
    #     test_file = OUTPUT_FILE
    #     data = {"x": 10, "y": 20}
    #     writeJson(test_file, data)

    #     with open(test_file, "r") as f:
    #         loaded = json.load(f)

    #     os.remove(test_file)
    #     self.assertEqual(loaded, data)

    def test_fuzzyMap(self):
        mapping = ["APPLE", "BANANA", "ORANGE"]
        print(fuzz.WRatio("appl", "APPLE"))
        print(fuzz.partial_ratio("appl", "APPLE"))

        # close match
        self.assertEqual(fuzzyMap("appl", mapping, score_bound=60), "APPLE")

        # no match above bound
        self.assertIsNone(fuzzyMap("zzz", mapping))

    def test_isValid(self):
        self.assertEqual(isValid("text"), "TEXT")
        self.assertEqual(isValid("  spaced  "), "SPACED")
        self.assertEqual(isValid(None, default="N/A"), "N/A")
        self.assertEqual(isValid(float("nan"), default=""), "")

    def test_parse_to_json(self):
        dic = parse_sheet_to_json(EXCEL_FILE, SCHEMA, DICTIONARY, OUTPUT_FILE, sheet_name=3)
        self.assertIsInstance(dic["df"], pd.DataFrame)
        print(dic["df"])
        print(dic["dat"])

if __name__ == "__main__":
    unittest.main()
