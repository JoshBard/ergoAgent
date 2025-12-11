from ruleset_consts import *

ROOM_RULES = {
    STERILIZATION: {
        "comments": (
            "Room type models: compact/enhanced/elite. "
            "Dimensions in inches; long axis grows with doors on long side."
        ),
        "dimensions": {
            "compact": {
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": 8,
                "baseWidthInches": 110,
                "baseLengthInches": 152,
                "additionalLongAxisPerDoorInches": 36
            },
            "enhanced": {
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": 14,
                "baseWidthInches": 110,
                "baseLengthInches": 184,
                "additionalLongAxisPerDoorInches": 36
            },
            "elite": {
                "treatmentRoomsMin": 15,
                "treatmentRoomsMax": 22,
                "baseWidthInches": 110,
                "baseLengthInches": 268,
                "additionalLongAxisPerDoorInches": 36
            },
            "largeOfficeStrategy": {
                "treatmentRoomsMin": 23,
                "note": "consider twoEnhanced or compactPlusElite"
            }
        },
        "shape": "rectangular",
        "orientation": {
            NARROW: {
                "layoutMode": NARROW,
                "axis": "long",
                "relationToClinicalCorridor": "perpendicular"
            },
            THREE_LAYER_CAKE: {
                "layoutMode": THREE_LAYER_CAKE,
                "axis": "long",
                "relationToClinicalCorridor": "parallel"
            },
            H_LAYOUT: {
                "layoutMode": H_LAYOUT,
                "relationToClinicalCorridor": "perpendicular",
                "connects": "clinicalCorridorsEndToEnd",
                "preferred": True
            }
        },
        "access": {
            "numberOfEntries": {
                "byTreatmentRooms": [
                    {"treatmentRoomsMin": 5, "treatmentRoomsMax": 8, "entries": 1},
                    {"treatmentRoomsMin": 9, "treatmentRoomsMax": 999, "entries": 2},
                ]
            },
            "entryLocationRules": [
                {
                    "description": "Clinical hallway egress must be direct",
                    "type": "required"
                },
                {
                    "description": "Doors connecting to clinical hallway must be at opposite ends of sterilization",
                    "type": "required"
                }
            ]
        },
        "clearances": {
            "adaDoorClearance": ADA_DOOR,
            "ideal": {
                "minDistanceFromCrossoverHallwayInches": 36
            }
        },
        "requiredWhen": "always",
        "adjacency": {
            "direct": [
                {"space": LAB, "condition": "ifAnalogLabExists"}
            ],
            "preferred": [
                {"space": CLINICAL_CORRIDOR}
            ],
            "mustNot": []
        },
        "visibility": {
            "mustNotBeVisibleFrom": [CLINICAL_CORRIDOR],
            "dirtySideMayBeMoreVisibleThanCleanSide": True
        },
        "scalability": "TBD"
    },

    LAB: {
        "comments": "THIS WILL NEED TO BE FLUSHED OUT IN DETAIL LATER",
        "dimensions": {
            "analogSmall": {
                "minimum": {"widthInches": 96, "lengthInches": 96}
            },
            "analogLarge": {
                "minimum": {"widthInches": 120, "lengthInches": 144}
            },
            "digitalSmall": {
                "minimum": {"widthInches": 120, "lengthInches": 120}
            },
            "hybridSmall": {
                "minimum": {"widthInches": 108, "lengthInches": 108}
            },
            "hybridOrDigitalLarge": {
                "minimum": {"widthInches": 168, "lengthInches": 120}
            }
        },
        "shape": "rectangular",
        "orientation": {
            NARROW: {
                "layoutMode": NARROW,
                "axis": "long",
                "relationToSterilization": "parallel",
                "connectionAxis": "short"
            },
            THREE_LAYER_CAKE: {
                "layoutMode": THREE_LAYER_CAKE,
                "axis": "long",
                "relationToSterilization": "parallel",
                "connectionAxis": "long"
            },
            H_LAYOUT: {
                "layoutMode": H_LAYOUT,
                "axis": "long",
                "relationToSterilization": "parallel",
                "connectionAxis": "long"
            }
        },
        "access": {
            "numberOfEntries": {"fixed": 1},
            "entryLocationRules": [
                {
                    "description": "Clinical hallway egress must not be direct",
                    "type": "required"
                }
            ]
        },
        "clearances": {
            "adaDoorClearance": ADA_DOOR
        },
        "requiredWhen": "userInput",
        "adjacency": {
            "direct": [],
            "preferred": [],
            "mustNot": [
                {"space": CONSULT},
                {"space": DUAL_ENTRY_TREATMENT},
                {"space": SIDE_TOE_TREATMENT},
                {"space": TOE_TREATMENT},
            ]
        },
        "visibility": {
            "mustBeVisibleFrom": [],
            "mustNotBeVisibleFrom": []
        },
        "scalability": "TBD"
    },

    CONSULT: {
        "comments": "1 entry required, 2 preferred if second entry comes off clinical or crossover hallway.",
        "dimensions": {
            "idealMatchesTreatmentRoom": True,
            "minimum": {"widthInches": 96, "lengthInches": 96},
            "livingRoomConsult": {"widthInches": 156, "lengthInches": 120}
        },
        "shape": "rectangular",
        "orientation": {
            NARROW: {"layoutMode": NARROW, "allowed": False},
            THREE_LAYER_CAKE: {"layoutMode": THREE_LAYER_CAKE, "allowed": True},
            H_LAYOUT: {"layoutMode": H_LAYOUT, "allowed": True}
        },
        "access": {
            "numberOfEntries": {
                "required": 1,
                "preferredMax": 2,
                "secondEntrySources": [CLINICAL_CORRIDOR, CROSSOVER_HALLWAY]
            },
            "entryLocationRules": [
                {"description": "One entry near check-out", "type": "required"},
                {"description": "One entry near clinical hallway", "type": "preferred"}
            ]
        },
        "clearances": {
            "adaDoorClearance": ADA_DOOR
        },
        "requiredWhen": "userInput",
        "adjacency": {
            "direct": [],
            "preferred": [
                {"space": CHECK_OUT, "maxDistanceFeet": 15}
            ],
            "mustNot": [
                {"space": MECHANICAL},
                {"space": LAB}
            ]
        },
        "visibility": {
            "mustBeVisibleFrom": [],
            "mustNotBeVisibleFrom": []
        },
        "scalability": "userInput"
    },

    PATIENT_RESTROOM: {
        "comments": "Scalability uses occupancy and square footage thresholds.",
        "dimensions": {
            "minimum": {"widthInches": 99, "lengthInches": 93}
        },
        "shape": "rectangular",
        "orientation": {
            NARROW: {"layoutMode": NARROW, "allowed": True},
            THREE_LAYER_CAKE: {"layoutMode": THREE_LAYER_CAKE, "allowed": True},
            H_LAYOUT: {"layoutMode": H_LAYOUT, "allowed": True}
        },
        "access": {
            "numberOfEntries": {"fixed": 1},
            "entryLocationRules": [
                {"description": "Must not be accessed from within another room", "type": "required"},
                {"description": "Ideally not located directly in the patient lounge", "type": "preferred"}
            ]
        },
        "clearances": {
            "adaDoorClearance": ADA_DOOR
        },
        "requiredWhen": "userInput",
        "adjacency": {
            "direct": [],
            "preferred": [
                {"space": CHECK_OUT, "maxDistanceFeet": 15}
            ],
            "mustNot": []
        },
        "visibility": {
            "mustBeVisibleFrom": [],
            "mustNotBeVisibleFrom": []
        },
        "scalability": {
            "bySquareFootage": [
                {"buildingSqFtMax": 1500, "minRestrooms": 1},
                {"buildingSqFtMin": 1501, "minRestrooms": 2}
            ],
            "byOccupancy": [
                {"occupantsMax": 50, "minRestrooms": 0},
                {"occupantsMin": 51, "rule": "addOneRestroomPer50Occupants"}
            ]
        }
    },

    CLINICAL_CORRIDOR: {
        "comments": "Main clinical circulation spine connecting treatment and support spaces.",
        "dimensions": {
            "width": {
                "minClearWidthInches": CORRIDOR_MIN_CLEAR_WIDTH_IN,
                "preferredMaxWidthInches": CORRIDOR_PREFERRED_MAX_WIDTH_IN
            }
        },
        "shape": "rectilinear",
        "orientation": {
            NARROW: {
                "layoutMode": NARROW,
                "description": "One continuous corridor spine with treatment rooms branching off"
            },
            THREE_LAYER_CAKE: {
                "layoutMode": THREE_LAYER_CAKE,
                "description": "Central spine flanked by treatment; sterilization and lab mid-corridor"
            },
            H_LAYOUT: {
                "layoutMode": H_LAYOUT,
                "description": "Two parallel corridor spines connected by crossover hallways"
            }
        },
        "access": {
            "crossoversRequiredEveryFeet": 60
        },
        "clearances": {
            "adaCorridorRuleset": "ADA ruleset for corridor width, turning radii, and passing spaces"
        },
        "requiredWhen": "treatmentRoomsPresent",
        "adjacency": {
            "direct": [
                {"space": DUAL_ENTRY_TREATMENT},
                {"space": SIDE_TOE_TREATMENT},
                {"space": TOE_TREATMENT},
                {"space": STERILIZATION},
                {"space": MOBILE_TECH},
                {"space": DOCTOR_NOOK},
                {"space": CROSSOVER_HALLWAY}
            ],
            "preferred": [
                {"space": CONSULT},
                {"space": PATIENT_RESTROOM}
            ],
            "mustNot": [
                {"space": PATIENT_LOUNGE, "relation": "terminatingInto"},
                {"space": RECEPTION, "relation": "terminatingInto"},
                {"space": STAFF_LOUNGE, "relation": "terminatingInto"},
                {"space": LAB, "relation": "directConnectionDiscouraged"},
                {"space": MECHANICAL, "relation": "directConnectionDiscouraged"}
            ]
        },
        "visibility": {
            "avoidVisibilityFrom": PATIENT_VISUAL_ZONES,
            "wayfindingFor": [PATIENT_RESTROOM, CONSULT]
        },
        "scalability": "corridorLengthAndCrossoversScaleWithTreatmentRooms"
    },

    DUAL_ENTRY_TREATMENT: {
        "comments": "Treatment room with two doorless openings on 12 o'clock headwall.",
        "dimensions": {
            "minimum": {"widthInches": 97, "lengthInches": 126},
            "ideal": {"widthInches": 100, "lengthInches": 126},
            "maximum": {"widthInches": 108, "lengthInches": 126}
        },
        "chair": {
            "orientation": "longAxis12To6",
            "twelveOclockWall": "headwall",
            "sixOclockWall": "toeWall",
            "threeOclockWall": "right",
            "nineOclockWall": "left"
        },
        "shape": "rectangular",
        "orientationLayout": {
            NARROW: {"layoutMode": NARROW, "allowed": True},
            THREE_LAYER_CAKE: {"layoutMode": THREE_LAYER_CAKE, "allowed": True},
            H_LAYOUT: {"layoutMode": H_LAYOUT, "allowed": True}
        },
        "access": {
            "numberOfEntries": {"fixed": 2},
            "entryLocationRules": [
                {
                    "description": "Two openings on 12 o'clock headwall, straddling chair head",
                    "type": "required"
                },
                {
                    "description": "Left opening toward 9 o'clock wall must be 36\" clear",
                    "type": "required",
                    "side": "left",
                    "minClearWidthInches": 36
                },
                {
                    "description": "Right opening toward 3 o'clock wall 25–36\" clear",
                    "type": "required",
                    "side": "right",
                    "minClearWidthInches": 25,
                    "typicalClearWidthInches": 28,
                    "maxClearWidthInches": 36
                },
                {
                    "description": "Headwall cabinet section between openings min 36\" clear",
                    "type": "required",
                    "minClearWidthInches": 36
                }
            ]
        },
        "clearances": {
            "doorType": "openingNoSwingDoor"
        },
        "requiredWhen": "treatmentRoomTypeDualEntrySelected",
        "adjacency": {
            "direct": [
                {"space": CLINICAL_CORRIDOR, "via": "leftOpening"},
                {"space": CLINICAL_CORRIDOR, "via": "rightOpening"}
            ],
            "preferred": [],
            "mustNot": [
                {"space": DUAL_ENTRY_TREATMENT, "relation": "directlyOppositeAcrossCorridor"}
            ]
        },
        "visibility": {
            "fromCorridor": "typical",
            "acousticConcernIfOpposing": True
        },
        "scalability": "TBD"
    }
}
