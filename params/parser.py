import pandas as pd # pyright: ignore[reportMissingModuleSource]
import json
from rapidfuzz import process, fuzz # pyright: ignore[reportMissingImports]

#CONFIG
EXCEL_FILE = "exampleParameters.xlsx"
SCHEMA = "parameters.json"
OUTPUT_FILE = "out.json"
DICTIONARY = "mapping.json"

#PARSING HELPERS

def parseSize(sizeStr):   #this will standardize 9x9,9'x9', 56"x56", 9'56"x9'56" ..etc --> [x,y] or [-1,-1] if empty
    if pd.isna(sizeStr) or sizeStr == "":
        return [-1, -1]
   
    s = str(sizeStr).upper()
    #print(s)
    s = s.replace('"',' ').replace("’", " ").replace("'", " ").replace("-", " ").replace("FT", " ").replace("IN", " ").replace("X", " ").replace("*", " ")
    #print(s)
    parts = s.split()
    #print(parts)
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
    return [-1, -1]

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
 
def fuzzyMap(input, mapping, score_bound=60):
    if not isinstance(input, str):
        return None

    input = input.strip().upper()
    mapping_upper = [m.upper() for m in mapping]

    best_match = process.extractOne(input, mapping_upper, scorer=fuzz.partial_ratio, score_cutoff=score_bound)
    
    return best_match[0] if best_match else None

def isValid(value, default=""):
    return default if pd.isna(value) else str(value).strip()

#Main Parser

def parse_sheet_to_json(excel_file, template_file, field_map_file, output_file):
    
    data = loadJson(template_file)

    #extract metadata
    meta_df = pd.read_excel(excel_file, nrows=5)
    data['clientName'] = isValid(meta_df.iloc[1,2])
    data['date'] = isValid(meta_df.iloc[2,2])
    data['projectType'] = isValid(meta_df.iloc[3,2])

    import re
    numbers = re.findall(r'\d+', str(meta_df.iloc[4,2]))
    if len(numbers) >= 2:
        data['projectSize'] = [float(numbers[0]), float(numbers[1])]
    elif len(numbers) == 1:
        data['projectSize'] = [float(numbers[0]), float(numbers[0])]
    else:
        data['projectSize'] = [-1, -1]

    #extract main table
    df = pd.read_excel(excel_file, sheet_name=0, header=5)
    mapping = loadJson(field_map_file)

    normCols(df)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    df['CATEGORIES'] = df['CATEGORIES'].ffill()
    df = df.drop(columns=[df.columns[0]])

    

    

    return df


#RUN
if __name__ == "__main__":
    parse_sheet_to_json(EXCEL_FILE, SCHEMA, DICTIONARY, OUTPUT_FILE)