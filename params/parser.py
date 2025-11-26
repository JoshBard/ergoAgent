import pandas as pd # pyright: ignore[reportMissingModuleSource]
import json
import re
from rapidfuzz import process, fuzz # pyright: ignore[reportMissingImports]
from datetime import datetime   
from dateutil import parser # pyright: ignore[reportMissingModuleSource]

#CONFIG
EXCEL_FILE = "exampleParameters.xlsx"
SCHEMA = "parameters.json"
OUTPUT_FILE = "out.json"
DICTIONARY = "mapping.json"

#PARSING HELPERS

def parseSize(sizeStr):   #this will standardize 9x9,9'x9', 56"x56", 9'56"x9'56" ..etc --> [x,y] or [-1,-1] if empty
    if pd.isna(sizeStr) or sizeStr == "":
        return [-1, -1]
   
    s = str(sizeStr).strip().upper()
    s = (
        s.replace('"',' ')
        .replace("’", " ")
        .replace("'", " ")
        .replace("-", " ")
        .replace("FT", " ")
        .replace("IN", " ")
        .replace("X", " ")
        .replace("*", " ")
    )

    parts = s.split()
    try:
        parts = [float(p) for p in parts]
    except Exception as e:
        print(f"An error occurred: {e}")
        return [-1,-1]
    
    if(len(parts) == 4):    #convert ft to inches (if 4 numbers present, assume first and second numbers are feet else assume both inches)
        return [parts[1] + (12*parts[0]), parts[3] + (12*parts[2])]
    elif(len(parts) == 2):
        return [parts[0],parts[1]]
    else:
        return [-1,-1]
    
def parse_date_to_yyyymmdd(date_str, day_first=False):
    #Parse a date string into YYYYMMDD format.
    if not date_str or str(date_str).strip() == "":
        return ""

    date_str_clean = str(date_str).strip()

    # Auto-detect day_first if not explicitly provided
    if day_first is None:
        # Look for numeric components
        numbers = re.findall(r'\d+', date_str_clean)
        if len(numbers) >= 3:
            first, second = int(numbers[0]), int(numbers[1])
            # If first > 12, it must be day
            if first > 12:
                day_first = True
            # If second > 12, it must be day
            elif second > 12:
                day_first = False
            else:
                # ambiguous, default to American style
                day_first = False
        else:
            day_first = False

    try:
        dt = parser.parse(date_str_clean, dayfirst=day_first, fuzzy=True)
        return dt.strftime("%Y%m%d")
    except (ValueError, TypeError):
        return ""

def normCols(df):
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    return df

def cleanTextCol(df, cols):
    for col in cols:
        if col in df:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df

def loadJson(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
    
def writeJson(file_path, dict):
    with open(file_path, "w") as f:
        json.dump(dict, f, indent=4)
 
def fuzzyMap(input, mapping, score_bound=60):#not used, get rid probably
    if not isinstance(input, str):
        return None

    input = input.strip().upper()
    mapping_upper = [m.upper() for m in mapping]

    best_match = process.extractOne(input, mapping_upper, scorer=fuzz.partial_ratio, score_cutoff=score_bound)
    
    return best_match[0] if best_match else None

def isValid(value, default=""):
    if pd.isna(value):
        return default
    elif default == "":
        return str(value).strip().upper()
    else:
        return float(str(value).strip())

#Main Parser

def parse_sheet_to_json(excel_file, template_file, field_map_file, output_file, sheet_name=0):
    
    data = loadJson(template_file)
    mapping = loadJson(field_map_file)

    #extract metadata
    meta_df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)

    #populate metadata
    data['clientName'] = isValid(meta_df.iloc[0,2])
    data['date'] = parse_date_to_yyyymmdd(meta_df.iloc[1,2])
    data['projectType'] = isValid(meta_df.iloc[2,2])

    numbers = re.findall(r'\d+', str(meta_df.iloc[3,2]))
    if len(numbers) >= 2:
        data['projectSize'] = [float(numbers[0]), float(numbers[1])]
    elif len(numbers) == 1:
        data['projectSize'] = [float(numbers[0]), float(numbers[0])]
    else:
        data['projectSize'] = [-1, -1]

    #extract main table
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=5)#ignores first few rows of metadata

    #cleanup main table
    normCols(df)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    df['CATEGORIES'] = df['CATEGORIES'].ffill()
    df = df.drop(columns=[df.columns[0]])

    #Parse to Json
    potty_count = 0 #💩💩
    for _, row in df.iterrows():
        #Get raw cell data
        cat_raw = row["CATEGORIES"].strip().upper()#already uppercase so maybe redundant but this makes it certain
        space_raw = row["SPACES"].strip().upper()
        qty_raw = row["QTY"]
        no_cell = row.iloc[3]
        no_raw = "" if pd.isna(no_cell) else str(no_cell).strip()     #Needed because no header isn't always present
        size_raw = row["SIZE"]
        people_raw = row["#_OF_PEOPLE"]
        com_raw = row["COMMENTS"]
        
        if (space_raw == "PRIVATE RESTROOM"):   #Chart has two private restrooms!!!👎Fix This🫩
            
            if potty_count == 0:
                space_raw = "PRIVATE RESTROOM A"
                potty_count += 1
            else:
                space_raw = "PRIVATE RESTROOM B"
            


        #Determine highest level mapping key
        if cat_raw in mapping:
            cat_map = mapping[cat_raw]
        else:
            continue

        if space_raw in cat_map:
            room_path = cat_map[space_raw]
        else:
            continue
        
        #target finds room in schema
        keys = room_path.split(".")
        target = data[keys[0]] 
        target = target[keys[1]]

        #use mapping headers to fill schema
        heads = mapping["HEADERS"]
        target[heads["QTY"]] = isValid(qty_raw, default=-1)
        target[heads["NO"]] = isValid(no_raw)
        target[heads["SIZE"]] = parseSize(size_raw)
        target[heads["#_OF_PEOPLE"]] = isValid(people_raw, default=-1)
        target[heads["COMMENTS"]] = isValid(com_raw)

    writeJson(output_file, data)    
    return {"df": df, "dat": data}


#RUN
if __name__ == "__main__":
    parse_sheet_to_json(EXCEL_FILE, SCHEMA, DICTIONARY, OUTPUT_FILE)
