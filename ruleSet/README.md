***
## JSON Schema Specifications:
***

### Rule Set

Format:
```
{
    "roomType": {
        "attribute1": "attribute details",
        "attribute2": "details",
        ...
    },
    ...
}
```
| Room Types                    |
| ------------------            |
| `sterilization                ` |
| `lab                          ` |
| `consult                      ` |
| `patientRestroom              ` |
| `treatmentCoordinationStation ` |
| `mobileTechArea               ` |
| `doctorsOnDeck                ` |
| `doctorsOffice                ` |
| `officeManagerOffice          ` |
| `businessOffice               ` |
| `altBusinessOffice            ` |
| `staffLounge                   `|
| `patientLounge                ` |
|` crossoverHallway             ` |
| `clinicalCorridor             ` |
| `adaLifeSafety                ` |
| `gpTreatment                  ` |

| Attribute         | Description                               |
| ----------------- | --------------------------------------    |
| `"dimensions"`      | ```{"ideal": [x,y]OR"none", "minimum": [x,y]OR"none", "maximum": [x,y]OR"none"}  ```    |
| `"shape" `          | ```"Rectangular"   ```                          |
| `"orientation" `    | ```{"narrow": ["reference","perpendicular OR parallel"]OR"none", "tlc": "    ", "h": "   "}``` |
| `"numberOfEntries"` | ```[[min bound, entries num], [ , ], ...] ```  |
| `"entryLocation" `  | ```[["rule", 1 OR 2 (req,pref)], [ , ], ...]  ```       |  
| `"clearancesADA" `  | ```[clearance width, count]OR"none"   ```       |
| `"clearancesIdeal"` |``` [clearance amount, "details"]     ```        |   !!!
| `"requirements"   ` | ```["details", "condition"]       ```           |   !!!
| `"adjacency"       `| ```{"direct": ["details"], "preferred": [], "seperation": []} ```   |   !!!
| `"visibility"    `  | ```{"required": "details", "not": " "}   ```    |
| `"scalability"   `  | !! No convention !!                       |   !!!

***
