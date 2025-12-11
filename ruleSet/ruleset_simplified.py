# ruleset.py

from ruleset_consts import (
    # layout modes
    NARROW,
    THREE_LAYER_CAKE,
    H_LAYOUT,
    # spaces
    STERILIZATION,
    LAB,
    CONSULT,
    PATIENT_RESTROOM,
    TREATMENT_COORDINATION,
    MOBILE_TECH,
    DOCTORS_ON_DECK,
    DOCTOR_OFFICE,
    DOCTOR_PRIVATE_RESTROOM,
    OFFICE_MANAGER,
    BUSINESS_OFFICE,
    ALT_BUSINESS_OFFICE,
    STAFF_LOUNGE,
    PATIENT_LOUNGE,
    CROSSOVER_HALLWAY,
    CLINICAL_CORRIDOR,
    DUAL_ENTRY_TREATMENT,
    SIDE_TOE_TREATMENT,
    TOE_TREATMENT,
    # supporting
    RECEPTION,
    CHECK_IN,
    CHECK_OUT,
    MECHANICAL,
    STAFF_ENTRY,
    STAFF_RESTROOMS,
    DOCTOR_NOOK,
    # groups
    PATIENT_VISUAL_ZONES,
    # ADA
    ADA_DOOR,
)

from ruleset_core import (
    # triggers (indexed)
    TRIGGER_ALWAYS,
    TRIGGER_USER_INPUT,
    TRIGGER_TREATMENT_ROOMS_PRESENT,
    TRIGGER_TREATMENT_ROOMS_GT_4,
    TRIGGER_TWO_PARALLEL_CLINICAL,
    TRIGGER_TREATMENT_ROOMS_GE_5_NO_DOCTOR_OFFICE,
    # rule kinds (indexed) for places we don't use helpers
    RULE_OPPOSITE_ENDS_ON_LONG_AXIS,
    RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR,
    RULE_ENTRY_FROM_ONE_OF,
    RULE_ENTRY_INTERNAL_CONNECTION,
    RULE_SEPARATE_FROM_ALL_OTHER_SPACES,
    RULE_PREFER_NEAR_CLINICAL_CENTER,
    RULE_PREFER_NEAR_TREATMENT_CENTER,
    RULE_NOT_TERMINATE_INTO,
    RULE_NOT_DIRECTLY_OPPOSITE_SAME_TYPE,
    RULE_TOE_SIDE_ENTRY_LOCATION_TBD,
    RULE_TOE_WALL_ENTRY_FROM,
    # helper constructors that already embed numeric kinds
    entry_from,
    entry_not_from,
    entry_within_distance,
    near_space,
    direct_adjacency,
    separate_from,
    avoid_visibility_from,
    require_visibility_from,
    not_within_distance_of,
)


ROOM_RULES = {
    # ---------------------------------------------------------
    # STERILIZATION
    # ---------------------------------------------------------
    STERILIZATION: {
        "comments": (
            "Compact/enhanced/elite models; long axis grows with doors along long side."
        ),
        "shape": "rectangular",
        "dimensions": {
            # [range of # of treatment rooms], [width, length], [extra 3 ft per door on long side]
            "compact": {
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": 8,
                "widthInches": 110,
                "lengthInches": 152,
                "extraLongAxisPerDoorInches": 36,
                "extraOnLongSide": True,
            },
            "enhanced": {
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": 14,
                "widthInches": 110,
                "lengthInches": 168,
                "extraLongAxisPerDoorInches": 36,
                "extraOnLongSide": True,
            },
            "elite": {
                "treatmentRoomsMin": 15,
                "treatmentRoomsMax": 22,
                "widthInches": 110,
                "lengthInches": 268,
                "extraLongAxisPerDoorInches": 36,
                "extraOnLongSide": True,
            },
        },
        "orientation": {
            NARROW: {
                "axis": "long",
                "relationToClinicalCorridor": "perpendicular",
            },
            THREE_LAYER_CAKE: {
                "axis": "long",
                "relationToClinicalCorridor": "parallel",
                "position": "centerOfClinical",
            },
            H_LAYOUT: {
                "relationToClinicalCorridor": "perpendicular",
                "connectsClinicalCorridorsEndToEnd": True,
            },
        },
        "entries": {
            # [[5,1], [9,2]]
            "byTreatmentRooms": [
                {"treatmentRoomsMin": 5, "treatmentRoomsMax": 8, "entries": 1},
                {"treatmentRoomsMin": 9, "treatmentRoomsMax": 999, "entries": 2},
            ]
        },
        "entryRules": [
            entry_from(CLINICAL_CORRIDOR, hard=True),
            {
                "kind": RULE_OPPOSITE_ENDS_ON_LONG_AXIS,
                "space": CLINICAL_CORRIDOR,
                "hard": True,
            },
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_ALWAYS,
        },
        "adjacencyRules": [
            {
                "kind": RULE_ENTRY_INTERNAL_CONNECTION,  # semantic: conditional adjacency to analogLab
                "target": "analogLab",
                "condition": "analogLabExists",
                "hard": False,
            },
            near_space(CLINICAL_CORRIDOR, max_distance_inches=0, hard=False),
        ],
        "visibilityRules": [
            avoid_visibility_from(CLINICAL_CORRIDOR, hard=False),
        ],
        "scalability": "considerChangingFromFirstEntryOfDimensions",
    },

    # ---------------------------------------------------------
    # LAB (TBD)
    # ---------------------------------------------------------
    LAB: {
        "comments": "Lab rules TBD; placeholder for adjacency and requirement hooks.",
        "shape": "rectangular",
        "dimensions": "TBD",
        "orientation": "TBD",
        "entries": "TBD",
        "entryRules": [],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [],
        "visibilityRules": [],
        "scalability": "TBD",
    },

    # ---------------------------------------------------------
    # CONSULT
    # ---------------------------------------------------------
    CONSULT: {
        "comments": "1 entry required; 2 preferred if second entry comes off clinical or crossover hallway.",
        "shape": "rectangular",
        "dimensions": {
            "idealMatchesTreatmentRoom": True,
            "minimum": {"widthInches": 96, "lengthInches": 96},
            "maximum": {"widthInches": 156, "lengthInches": 120},
        },
        "orientation": {
            NARROW: {"allowed": False},
            THREE_LAYER_CAKE: {"allowed": True},
            H_LAYOUT: {"allowed": True},
        },
        "entries": {
            "minEntries": 1,
            "preferredMaxEntries": 2,
        },
        "entryRules": [
            entry_within_distance(CHECK_OUT, max_distance_inches=15 * 12, hard=True),
            entry_from(CLINICAL_CORRIDOR, hard=False),
            entry_from(CROSSOVER_HALLWAY, hard=False),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            near_space(CHECK_OUT, max_distance_inches=15 * 12, hard=True),
            separate_from(MECHANICAL, hard=True),
            separate_from(LAB, hard=True),
        ],
        "visibilityRules": [],
        "scalability": "userInput",
    },

    # ---------------------------------------------------------
    # PATIENT RESTROOM
    # ---------------------------------------------------------
    PATIENT_RESTROOM: {
        "comments": "Scalability: count driven by building area and occupancy.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 99, "lengthInches": 93},
            "maximum": None,
        },
        "orientation": {
            NARROW: {"allowed": True},
            THREE_LAYER_CAKE: {"allowed": True},
            H_LAYOUT: {"allowed": True},
        },
        "entries": {
            "minEntries": 1,
        },
        "entryRules": [
            {
                "kind": RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR,
                "hard": True,
            },
            entry_not_from(PATIENT_LOUNGE, hard=False),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            near_space(CHECK_OUT, max_distance_inches=15 * 12, hard=False),
        ],
        "visibilityRules": [],
        "scalability": {
            "bySquareFootage": [
                {"buildingSqFtMax": 1500, "minRestrooms": 1},
                {"buildingSqFtMin": 1501, "minRestrooms": 2},
            ],
            "byOccupancy": [
                {"occupantsMax": 50, "minRestrooms": 0},
                {
                    "rule": "addOneRestroomPer50OccupantsAfterFirst50",
                    "baseOccupants": 50,
                },
            ],
        },
    },

    # ---------------------------------------------------------
    # TREATMENT COORDINATION STATION
    # ---------------------------------------------------------
    TREATMENT_COORDINATION: {
        "comments": "Only boundaries + entrances modeled.",
        "shape": "rectangular",
        "dimensions": {
            "minimumByOperators": [
                {"operators": 1, "widthInches": 42, "lengthInches": 54},
                {"operators": 2, "widthInches": 42, "lengthInches": 90},
            ],
            "maximum": None,
        },
        "orientation": {
            NARROW: {"relationToClinicalCorridor": "parallel"},
            THREE_LAYER_CAKE: {"relationToClinicalCorridor": "parallel"},
            H_LAYOUT: {"relationToClinicalCorridor": "parallel"},
        },
        "entries": "TBD",
        "entryRules": [
            {
                "kind": RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR,
                "hard": True,
            },
            entry_not_from(PATIENT_LOUNGE, hard=False),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            {
                "kind": RULE_PREFER_NEAR_CLINICAL_CENTER,
                "hard": False,
            },
            separate_from(PATIENT_RESTROOM, hard=False),
        ],
        "visibilityRules": [],
        "scalability": "TBD",
    },

    # ---------------------------------------------------------
    # MOBILE TECH AREA
    # ---------------------------------------------------------
    MOBILE_TECH: {
        "comments": "Mobile tech cluster; only envelope + access relations modeled.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 42, "lengthInches": 84},
            "maximum": None,
        },
        "orientation": {
            NARROW: {"relationToClinicalCorridor": "parallel"},
            THREE_LAYER_CAKE: {"relationToClinicalCorridor": "parallel"},
            H_LAYOUT: {"relationToClinicalCorridor": "parallel"},
        },
        "entries": "TBD",
        "entryRules": [
            {
                "kind": RULE_ENTRY_FROM_ONE_OF,
                "spaces": ["sterilizationCorridor", CLINICAL_CORRIDOR],
                "hard": True,
            },
            entry_not_from(CROSSOVER_HALLWAY, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_ALWAYS,
        },
        "adjacencyRules": [
            {
                "kind": RULE_PREFER_NEAR_CLINICAL_CENTER,
                "hard": False,
            },
            separate_from(CROSSOVER_HALLWAY, hard=True),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
        ],
        "visibilityRules": [
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
        ],
        "scalability": {
            "driver": "treatmentRooms",
            "clusters": [
                {"minTreatmentRooms": 1, "maxTreatmentRooms": 5, "count": 1},
                {"minTreatmentRooms": 6, "maxTreatmentRooms": 10, "count": 2},
            ],
        },
    },

    # ---------------------------------------------------------
    # DOCTORS ON DECK
    # ---------------------------------------------------------
    DOCTORS_ON_DECK: {
        "comments": "Doctor nook; 1 or 2 providers.",
        "shape": "rectangular",
        "dimensions": {
            "variants": [
                {"name": "single", "widthInches": 66, "lengthInches": 90},
                {"name": "dual", "widthInches": 66, "lengthInches": 114},
                {"name": "longDual", "widthInches": 90, "lengthInches": 102},
            ]
        },
        "orientation": {
            NARROW: {"relationToClinicalCorridor": "along"},
            THREE_LAYER_CAKE: {"relationToClinicalCorridor": "along"},
            H_LAYOUT: {"relationToClinicalCorridor": "along"},
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            entry_from(CLINICAL_CORRIDOR, hard=True),
            entry_not_from(PATIENT_LOUNGE, hard=True),
            entry_not_from(RECEPTION, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_TREATMENT_ROOMS_GE_5_NO_DOCTOR_OFFICE,
        },
        "adjacencyRules": [
            direct_adjacency(CLINICAL_CORRIDOR, hard=True),
            {
                "kind": RULE_PREFER_NEAR_TREATMENT_CENTER,
                "hard": False,
            },
            near_space(CONSULT, max_distance_inches=None, hard=False),
            separate_from(STAFF_LOUNGE, hard=True),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
        ],
        "visibilityRules": [
            require_visibility_from(CLINICAL_CORRIDOR, hard=True),
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
        ],
        "scalability": {
            "driver": "treatmentRooms",
            "variants": [
                {"name": "single", "minTreatmentRooms": 1},
                {"name": "dual", "minTreatmentRooms": 7},
            ],
        },
    },

    # ---------------------------------------------------------
    # DOCTOR OFFICE
    # ---------------------------------------------------------
    DOCTOR_OFFICE: {
        "comments": "Private/shared doctor office; restroom handled as separate room.",
        "shape": "rectangular",
        "dimensions": {
            "variants": [
                {"name": "single", "widthInches": 96, "lengthInches": 96},
                {"name": "twoThree", "widthInches": 120, "lengthInches": 156},
                # 3+ left as TBD for area calc
            ]
        },
        "orientation": {
            NARROW: {"relationToClinicalCorridor": "along"},
            THREE_LAYER_CAKE: {"relationToClinicalCorridor": "along"},
            H_LAYOUT: {"relationToSecondCrossoverHallway": "along"},
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            {
                "kind": RULE_ENTRY_FROM_ONE_OF,
                "spaces": [CLINICAL_CORRIDOR, "secondCrossoverHallwayHLayout"],
                "hard": True,
            },
            entry_not_from(PATIENT_LOUNGE, hard=True),
            entry_not_from(RECEPTION, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            {
                "kind": RULE_ENTRY_INTERNAL_CONNECTION,
                "target": DOCTOR_PRIVATE_RESTROOM,
                "hard": False,
            },
            {
                "kind": RULE_PREFER_NEAR_TREATMENT_CENTER,
                "hard": False,
            },
            near_space(CONSULT, max_distance_inches=None, hard=False),
            separate_from(STAFF_LOUNGE, hard=True),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
        ],
        "visibilityRules": [],
        "scalability": "TBD",
    },

    # ---------------------------------------------------------
    # DOCTOR PRIVATE RESTROOM
    # ---------------------------------------------------------
    DOCTOR_PRIVATE_RESTROOM: {
        "comments": "Private restroom; only direct from doctorOffice.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 60, "lengthInches": 60},
            "maximum": None,
        },
        "orientation": {
            NARROW: {"allowed": True},
            THREE_LAYER_CAKE: {"allowed": True},
            H_LAYOUT: {"allowed": True},
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            entry_from(DOCTOR_OFFICE, hard=True),
            {
                "kind": RULE_SEPARATE_FROM_ALL_OTHER_SPACES,  # semantic: no other entry sources
                "hard": True,
            },
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            direct_adjacency(DOCTOR_OFFICE, hard=True),
            {
                "kind": RULE_SEPARATE_FROM_ALL_OTHER_SPACES,
                "hard": True,
            },
        ],
        "visibilityRules": [],
        "scalability": "none",
    },

    # ---------------------------------------------------------
    # OFFICE MANAGER OFFICE
    # ---------------------------------------------------------
    OFFICE_MANAGER: {
        "comments": "Front-of-house management office near reception/business office.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 90, "lengthInches": 66},
            "maximum": {"widthInches": 96, "lengthInches": 96},
        },
        "orientation": {
            NARROW: {"allowed": True},
            THREE_LAYER_CAKE: {"allowed": True},
            H_LAYOUT: {"allowed": True},
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            entry_within_distance(CHECK_IN, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(CHECK_OUT, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(BUSINESS_OFFICE, max_distance_inches=10 * 12, hard=True),
            entry_not_from(PATIENT_LOUNGE, hard=True),
            entry_not_from(PATIENT_RESTROOM, hard=False),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_ALWAYS,
        },
        "adjacencyRules": [
            near_space(RECEPTION, max_distance_inches=10 * 12, hard=False),
            near_space(BUSINESS_OFFICE, max_distance_inches=10 * 12, hard=False),
            separate_from("treatmentRoom", hard=True),
            separate_from(STERILIZATION, hard=True),
            separate_from(LAB, hard=True),
        ],
        "visibilityRules": [
            avoid_visibility_from("waitingRoom", hard=True),
        ],
        "scalability": {"minCount": 1, "maxCount": 1},
    },

    # ---------------------------------------------------------
    # BUSINESS OFFICE
    # ---------------------------------------------------------
    BUSINESS_OFFICE: {
        "comments": "Back-of-reception office for billing/admin.",
        "shape": "rectangular",
        "dimensions": {
            "variants": [
                {"name": "small", "widthInches": 90, "lengthInches": 96},
                {"name": "medium", "widthInches": 114, "lengthInches": 96},
                {"name": "large", "widthInches": 114, "lengthInches": 144},
            ]
        },
        "orientation": {
            NARROW: {"allowed": True},
            THREE_LAYER_CAKE: {"allowed": True},
            H_LAYOUT: {"allowed": True},
        },
        "entries": {
            "allowedEntryCounts": [1, 2],
        },
        "entryRules": [
            entry_within_distance(RECEPTION, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(CHECK_IN, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(CHECK_OUT, max_distance_inches=10 * 12, hard=True),
            entry_not_from(PATIENT_RESTROOM, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_TREATMENT_ROOMS_GT_4,
        },
        "adjacencyRules": [
            direct_adjacency(RECEPTION, hard=False),
            direct_adjacency(CHECK_IN, hard=False),
            direct_adjacency(CHECK_OUT, hard=False),
            near_space(OFFICE_MANAGER, max_distance_inches=None, hard=False),
            separate_from("treatmentRoom", hard=True),
            separate_from(STERILIZATION, hard=True),
            separate_from(LAB, hard=True),
            separate_from(PATIENT_RESTROOM, hard=True),
        ],
        "visibilityRules": [
            require_visibility_from(RECEPTION, hard=False),
            require_visibility_from(CHECK_IN, hard=False),
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
        ],
        "scalability": {
            "driver": "treatmentRooms",
            "variants": [
                {"name": "small", "maxTreatmentRooms": 6},
                {"name": "medium", "minTreatmentRooms": 7, "maxTreatmentRooms": 10},
                {"name": "large", "minTreatmentRooms": 11, "maxTreatmentRooms": 15},
                {"name": "commandCenter", "minTreatmentRooms": 12},
            ],
        },
    },

    # ---------------------------------------------------------
    # ALT BUSINESS OFFICE
    # ---------------------------------------------------------
    ALT_BUSINESS_OFFICE: {
        "comments": "Alternative business office; workstation-based capacity.",
        "shape": "rectangular",
        "dimensions": "TBD",
        "orientation": {
            NARROW: {"relationToReceptionCheckIn": "behind"},
            THREE_LAYER_CAKE: {"relationToCheckOut": "adjacent"},
            H_LAYOUT: "TBD",
        },
        "entries": {
            "allowedEntryCounts": [1, 2],
        },
        "entryRules": [
            entry_within_distance(RECEPTION, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(CHECK_IN, max_distance_inches=10 * 12, hard=True),
            entry_within_distance(CHECK_OUT, max_distance_inches=10 * 12, hard=True),
            entry_not_from(PATIENT_LOUNGE, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
            "ideal": [
                not_within_distance_of(CROSSOVER_HALLWAY, 36, hard=False),
            ],
        },
        "requirements": {
            "trigger": TRIGGER_TREATMENT_ROOMS_GT_4,
        },
        "adjacencyRules": [
            direct_adjacency(RECEPTION, hard=False),
            direct_adjacency(CHECK_IN, hard=False),
            direct_adjacency(CHECK_OUT, hard=False),
            near_space(OFFICE_MANAGER, max_distance_inches=None, hard=False),
            separate_from("treatmentRoom", hard=True),
            separate_from(STERILIZATION, hard=True),
            separate_from(LAB, hard=True),
            separate_from(PATIENT_RESTROOM, hard=True),
        ],
        "visibilityRules": [
            require_visibility_from(RECEPTION, hard=False),
            require_visibility_from(CHECK_IN, hard=False),
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
        ],
        "scalability": {
            "driver": "treatmentRooms",
            "workstations": [
                {"label": "two/three", "minTreatmentRooms": 1},
                {"label": "four/six", "minTreatmentRooms": 7},
                {"label": "sevenPlus", "minTreatmentRooms": 13},
            ],
        },
    },

    # ---------------------------------------------------------
    # STAFF LOUNGE
    # ---------------------------------------------------------
    STAFF_LOUNGE: {
        "comments": "Staff-only lounge; fully concealed from patient zones.",
        "shape": "rectangular",
        "dimensions": {
            "perSeatAreaSqIn": 4032,
        },
        "orientation": {
            NARROW: {"relationToPatientZone": "far"},
            THREE_LAYER_CAKE: {"relationToClinicalCorridor": "back"},
            H_LAYOUT: "TBD",
        },
        "entries": {
            "allowedEntryCounts": [1, 2],
        },
        "entryRules": [
            entry_from("staffCorridor", hard=True),
            entry_not_from(PATIENT_LOUNGE, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_ALWAYS,
        },
        "adjacencyRules": [
            near_space(STAFF_ENTRY, max_distance_inches=None, hard=False),
            near_space(STAFF_RESTROOMS, max_distance_inches=None, hard=False),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
            separate_from(CHECK_IN, hard=True),
        ],
        "visibilityRules": [
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
        ],
        "scalability": {
            "seat": ["4032 net square inches", "treatmentRoom"],
            "kitchenette": "TBD",
            "locker": "TBD",
        },
    },

    # ---------------------------------------------------------
    # PATIENT LOUNGE
    # ---------------------------------------------------------
    PATIENT_LOUNGE: {
        "comments": "Waiting/lounge zone at front of house; scaled by treatment room count.",
        "shape": "rectangular",
        "dimensions": {
            "perSeatAreaSqIn": 4320,
        },
        "orientation": {
            NARROW: {"relationToFront": "close"},
            THREE_LAYER_CAKE: "TBD",
            H_LAYOUT: "TBD",
        },
        "entries": {
            "allowedEntryCounts": [1, 2],
        },
        "entryRules": [
            entry_from(RECEPTION, hard=True),
            entry_from(CHECK_IN, hard=True),
            entry_not_from(CLINICAL_CORRIDOR, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_ALWAYS,
        },
        "adjacencyRules": [
            direct_adjacency(RECEPTION, hard=True),
            direct_adjacency(CHECK_IN, hard=True),
            near_space(PATIENT_RESTROOM, max_distance_inches=20 * 12, hard=False),
            separate_from(STAFF_LOUNGE, hard=True),
            separate_from(STERILIZATION, hard=True),
            separate_from(LAB, hard=True),
            separate_from(MECHANICAL, hard=True),
        ],
        "visibilityRules": [
            require_visibility_from("receptionDesk", hard=True),
            require_visibility_from("entry", hard=True),
            avoid_visibility_from(CLINICAL_CORRIDOR, hard=True),
        ],
        "scalability": {
            "driver": "treatmentRooms",
            "seatsPerTreatmentRoom": 1.5,
        },
    },

    # ---------------------------------------------------------
    # CROSSOVER HALLWAY
    # ---------------------------------------------------------
    CROSSOVER_HALLWAY: {
        "comments": "Connector between parallel clinical corridors.",
        "shape": "rectangular",
        "dimensions": {
            "minimumWidthInches": 60,
            "preferredMaxWidthInches": 72,
        },
        "orientation": {
            NARROW: "none",
            THREE_LAYER_CAKE: "none",
            H_LAYOUT: {"relationToClinicalHallways": "between"},
        },
        "entries": {
            "minEntries": 2,
        },
        "entryRules": [
            entry_from(CLINICAL_CORRIDOR, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_TWO_PARALLEL_CLINICAL,
        },
        "adjacencyRules": [
            direct_adjacency(CLINICAL_CORRIDOR, hard=True),
            separate_from(STAFF_LOUNGE, hard=True),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
            separate_from(CHECK_IN, hard=True),
            separate_from(CHECK_OUT, hard=True),
        ],
        "visibilityRules": [
            avoid_visibility_from("entry", hard=True),
            avoid_visibility_from("lounge", hard=True),
            avoid_visibility_from("reception", hard=True),
            avoid_visibility_from(STERILIZATION, hard=True),
            avoid_visibility_from("treatment", hard=True),
            avoid_visibility_from("restrooms", hard=True),
        ],
        "scalability": {
            "minCount": 1,
            "corridorLengthInchesPerCrossover": 7200,
        },
    },

    # ---------------------------------------------------------
    # CLINICAL CORRIDOR
    # ---------------------------------------------------------
    CLINICAL_CORRIDOR: {
        "comments": "Main clinical circulation spine.",
        "shape": "rectilinear",
        "dimensions": {
            "minimumWidthInches": 60,
            "preferredMaxWidthInches": 72,
        },
        "orientation": {
            NARROW: {"description": "continuous"},
            THREE_LAYER_CAKE: "none",
            H_LAYOUT: {"relationToClinicalCorridor": "parallel"},
        },
        "entries": {
            "minEntries": 2,
        },
        "entryRules": [
            {
                "kind": RULE_NOT_TERMINATE_INTO,
                "spaces": [PATIENT_LOUNGE, RECEPTION, STAFF_LOUNGE],
                "hard": True,
            }
        ],
        "clearances": {
            "adaCorridorRuleset": "ADA ruleset for corridor width",
        },
        "requirements": {
            "trigger": TRIGGER_TREATMENT_ROOMS_PRESENT,
        },
        "adjacencyRules": [
            direct_adjacency(DUAL_ENTRY_TREATMENT, hard=True),
            direct_adjacency(SIDE_TOE_TREATMENT, hard=True),
            direct_adjacency(TOE_TREATMENT, hard=True),
            direct_adjacency(STERILIZATION, hard=True),
            direct_adjacency(MOBILE_TECH, hard=True),
            direct_adjacency(DOCTOR_NOOK, hard=False),
            direct_adjacency(CROSSOVER_HALLWAY, hard=True),
            near_space(CONSULT, max_distance_inches=None, hard=False),
            near_space(PATIENT_RESTROOM, max_distance_inches=None, hard=False),
            separate_from(PATIENT_LOUNGE, hard=True),
            separate_from(RECEPTION, hard=True),
            separate_from(STAFF_LOUNGE, hard=True),
            separate_from(LAB, hard=False),
            separate_from(MECHANICAL, hard=False),
        ],
        "visibilityRules": [
            avoid_visibility_from(PATIENT_VISUAL_ZONES, hard=True),
            require_visibility_from(PATIENT_RESTROOM, hard=False),
            require_visibility_from(CONSULT, hard=False),
        ],
        "scalability": "treatment",
    },

    # ---------------------------------------------------------
    # DUAL ENTRY TREATMENT
    # ---------------------------------------------------------
    DUAL_ENTRY_TREATMENT: {
        "comments": "Two headwall openings; envelope + two entries.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 97, "lengthInches": 126},
            "ideal": {"widthInches": 100, "lengthInches": 126},
            "maximum": {"widthInches": 108, "lengthInches": 126},
        },
        "orientation": {
            NARROW: "continuous",
            THREE_LAYER_CAKE: "none",
            H_LAYOUT: "none",
        },
        "entries": {
            "minEntries": 2,
            "maxEntries": 2,
        },
        "entryRules": [
            entry_from(CLINICAL_CORRIDOR, hard=True),
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,  # or "none" if you gate it elsewhere
        },
        "adjacencyRules": [
            direct_adjacency(CLINICAL_CORRIDOR, hard=True),
            {
                "kind": RULE_NOT_DIRECTLY_OPPOSITE_SAME_TYPE,
                "space": DUAL_ENTRY_TREATMENT,
                "hard": True,
            },
        ],
        "visibilityRules": [],
        "scalability": "none",
    },

    # ---------------------------------------------------------
    # SIDE TOE TREATMENT
    # ---------------------------------------------------------
    SIDE_TOE_TREATMENT: {
        "comments": "Single side-toe entry; envelope + single entry.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 97, "lengthInches": 132},
            "ideal": {"widthInches": 100, "lengthInches": 132},
            "maximum": {"widthInches": 108, "lengthInches": 132},
        },
        "orientation": {
            NARROW: "continuous",
            THREE_LAYER_CAKE: "none",
            H_LAYOUT: "none",
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            {
                "kind": RULE_TOE_SIDE_ENTRY_LOCATION_TBD,
                "hard": False,
            }
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            direct_adjacency(CLINICAL_CORRIDOR, hard=True),
        ],
        "visibilityRules": [],
        "scalability": "none",
    },

    # ---------------------------------------------------------
    # TOE TREATMENT
    # ---------------------------------------------------------
    TOE_TREATMENT: {
        "comments": "Toe wall entry from corridor; envelope + single entry.",
        "shape": "rectangular",
        "dimensions": {
            "minimum": {"widthInches": 97, "lengthInches": 132},
            "ideal": {"widthInches": 100, "lengthInches": 132},
            "maximum": {"widthInches": 108, "lengthInches": 132},
        },
        "orientation": {
            NARROW: "continuous",
            THREE_LAYER_CAKE: "none",
            H_LAYOUT: "none",
        },
        "entries": {
            "minEntries": 1,
            "maxEntries": 1,
        },
        "entryRules": [
            {
                "kind": RULE_TOE_WALL_ENTRY_FROM,
                "space": CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
        "clearances": {
            "adaDoor": ADA_DOOR,
        },
        "requirements": {
            "trigger": TRIGGER_USER_INPUT,
        },
        "adjacencyRules": [
            direct_adjacency(CLINICAL_CORRIDOR, hard=True),
        ],
        "visibilityRules": [],
        "scalability": "none",
    },
}
