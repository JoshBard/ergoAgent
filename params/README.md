# `desergo/params` - Parameter Parsing Module

This directory contains all components required for converting client-supplied **hand-off sheets** (Excel workbooks) into a consistent, machine-readable **JSON parameter schema**. It includes the parsing library, schema definitions, field-mapping rules, a processing script, and a unit-tested test suite.

***

## Purpose

The goal of this module is to:
- **Ingest** client supplied `.xlsx` sheets
- **Validate** that each sheet is the correct format
- **Normalize and Parse** relevant data
- **Map** spreadsheet to JSON keys
- **Output** standardized JSON files

The pipeline is centered around `parser.py`, which handles row-level parsing, cleaning, formatting, and schema population. `processParams.py` acts as a batch processor that scans directories, validates sheets, and generates JSON output in bulk.

***

## Directory Structure
```
desergo/params
    mapping.json
    parameters.json
    parser.py
    processParams.py
    tests.py
    README.md
```
***
## Key Components
***

### `parser.py` - Parsing Library

Contains reusable parsing helpers and the main `parse_sheet_to_json()` routine.
Responsibilities include:

- **Cleaning / normalizing** column names
- **Parsing** flexible formats - dates, sizes, and numbers as strings
    - sizes (ft/in) -> [x,y](in)
    - dates (a/b/c, b/a/c, - or /, written out months) -> yyyymmdd
    - numbers (usually int but sometimes string) -> int
- **Mapping** spreadsheet rows into the JSON schema using mapping.json
    - robust disambiguation for same name rows and unlabled columns
- **Exporting** fully structured JSON

***

### `processParams.py` - Directory Batch Processor

CLI tool for batch ingestion of data

 - Scans input directory for `.xlsx` files
 - Validates each sheet via `isSheetValid()` (very minimal validation done in V1)
 - Invokes `parser.py::parse_sheet_to_json()` on valid files
 - Writes outputs to a new folder `{inputDir}/jsonParams/' that is creasted if it doesn't exist already
 - Logs validation/parse issues to sheet_validation.log
 - **Note:** `/jsonParams/` and `sheet_validation.log` are listed on `.gitignore`

***

### `tests.py` - Unit Test Suite

Covers:

- Size parsing
- Date parsing & auto day-first detection
- Column normalization
- Text cleaning
- JSON load/write helpers
- Fuzzy mapping
- Full parse_sheet_to_json call against test files
- Special restroom assignment logic (A/B disambiguation)

Run Test Suite:
```
python tests.py
```
- **Note:** uses some syntax unique to python3
- **Note:** tests output to `testout.json`, which is included in the `.gitignore`
- **Note:** can auto delete testout.json by toggling comment on `os.remove(OUTPUT_FILE)` in `tests.py::test_parse_to_json()`.

***

### `parameters.json` - Output Schema

Defines the full JSON structure after parsing, including:
- Metadata
    - clientName, date, projectType, projectSize
- Nested Sections
- Default values for expected fields
- Structure parsed values will be written to

The schema is generally:
```
{
    "metaData": ""
    ...
    "public":{
        "roomType":     {"qty": -1, "no": "", "size": [-1,-1], "people": -1, "com": ""},
        ...
    },
    "clinical":{
        ...
    },
    "private":{
        ...
    }
}
```

The `metaData` is structured as follows:
```
{
    "clientName": "",
    "date": "",
    "projectType": "",
    "projectSize": [-1, -1],
    ...
}
```

| `roomTypes` expected                   |
| ------------------            |
|`public.vestibule`|
|`public.patientLounge`|
|`public.patientRestroom`|
|`public.childrensArea`|
|`public.refreshmentArea`|
|`public.retailArea`|
|`public.checkIn`|
|`public.checkOut`|
|`public.consult`|
|`public.imaging`|
|`public.photoRoom`|
|`public.multiStalls`|
|`public.toyArea"
|`clinical.treatment`|
|`clinical.universal`|
|`clinical.hygiene`|
|`clinical.private`|
|`clinical.surgical`|
|`clinical.openBay`|
|`clinical.mobileTechArea`|
|`clinical.treatmentCoordinator`|
|`clinical.brushingStation`|
|`clinical.recovery`|
|`clinical.records`|
|`private.staffLounge`|
|`private.changingRoom`|
|`private.nursingRoom`|
|`private.laundry`|
|`private.staffRestroom`|
|`private.sterilization`|
|`private.lab`|
|`private.serverCloset`|
|`private.mechanical`|
|`private.janitorCloset`|
|`private.medGas`|
|`private.storageCloset`|
|`private.shipRec`|
|`private.conferenceRoom`|
|`private.doctorOffice`|
|`private.doctorPrivateRestroom`|
|`private.associatesOffice`|
|`private.associatesPrivateRestroom`|
|`private.doctorNook`|
|`private.officeManager`|
|`private.marketing`|
|`private.businessOffice`|
|`private.teamLeader`|
|`private.patientCareCenter`|

***

### `mapping.json` - Header & Category Mapping

Includes:

- Category → path mappings (e.g., “CLINICAL → universal → qty”)
- Header → key mappings for qty, no, size, people, comments

This file controls how spreadsheet rows map into the schema.

***

## Typical Workflow

1. Place client `.xlsx` sheets in a folder
2. Run `processParams.py` on the folder
3. Valid sheets → parsed into JSON under `jsonParams/`
4. Inspect logs for skipped sheets or warnings

***

## Notes & Assumptions

* The first worksheet rows contain metadata (client name, date, project type, project size).
* Private restrooms are automatically split into **A** and **B** based on encounter order.
* Notes collumn is assumed with iloc when "No" header is absent
* Column normalization aggressively uppercases and trims headers for stability.
* Date parsing supports noisy human inputs (e.g., “on Nov 21st 2025”).
* Malformed or unrelated sheets are safely skipped with a logged warning.