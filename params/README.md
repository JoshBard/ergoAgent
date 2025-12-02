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

***

### `processParams.py` - Directory Batch Processor

***

### `parameters.json` - Output Schema

***

### `mapping.json` - Header & Category Mapping

***

### `tests.py` - Unit Test Suite

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