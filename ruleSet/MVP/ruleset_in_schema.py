"""
ruleset_in_schema.py

Canonical ruleset encoded using RoomSchema and DSL enums from core.py.

This file defines one schema-conformant rule object per room type.
Each room definition maps abstract architectural rules into a
machine-readable, solver-friendly format.

NOTE:
- Geometry here refers ONLY to room envelope / outline
- No internal zoning, furniture, or equipment constraints
- Visibility is abstract (room-to-room only)
- TODO flags indicate missing information from source rules
- Every room must conform to RoomSchema
- All enums MUST come from core.py
- Use SPACE_GROUP where possible to avoid adjacency explosion
"""

from core import *
from ruleset_schema import RoomSchema


#Sterilization

STERILIZATION_RULES = {
    "identity": {
        "roomType": SPACE_ID.STERILIZATION,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Central sterilization and instrument processing space",
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "compact",
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": 8,
                "widthInches": 110,   # 9'-2"
                "lengthInches": 152,  # 12'-8"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,
            },
            {
                "label": "enhanced",
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": 14,
                "widthInches": 110,
                "lengthInches": 184,  # 15'-4"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,
            },
            {
                "label": "elite",
                "treatmentRoomsMin": 15,
                "treatmentRoomsMax": 22,
                "widthInches": 110,
                "lengthInches": 268,  # 22'-4"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": 8,
                "minEntries": 1,
                "maxEntries": 1,
            },
            {
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": None,
                "minEntries": 2,
                "maxEntries": 2,
            },
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_OPPOSITE_ENDS,
                "target": None,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": 36,
                "hard": False,
            },
        ],
        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
            {
                "target": SPACE_ID.LAB,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 1.0,
            }
        ],
        "separation": [],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [SPACE_ID.CLINICAL_CORRIDOR],
        "mustNotTerminateInto": [],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 1.0,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.5,
        },
    },
}

# Lab

LAB_RULES = {
    "identity": {
        "roomType": SPACE_ID.LAB,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Clinical laboratory supporting sterilization and treatment operations",
    },

    "existence": {
        # Assumption:
        # Labs are common but not universally required.
        # Often dependent on practice type or analog workflows.
        "trigger": TRIGGER_ENUM.DERIVED,  # TODO: confirm if always required in some practices
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,          # allow absence
                "max": 1,          # assume single shared lab
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        # Assumption:
        # Labs are typically rectilinear or rectangular.
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                "label": "default_lab",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": None,     # TODO: define minimum lab width
                "lengthInches": None,    # TODO: define minimum lab length
                "areaSqIn": None,        # TODO: preferred area if known
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            }
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        # Assumption:
        # Labs are flexible and adapt to most layouts.
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],

        "entryConstraints": [
            {
                # Assumption:
                # Labs typically connect to clinical circulation.
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],

        "ada": {
            # Assumption:
            # Treat lab like other staff-accessible rooms.
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Inferred from sterilization rules:
                # Lab is often adjacent to sterilization when present.
                "target": SPACE_ID.STERILIZATION,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": False,
            }
        ],

        "preferredProximity": [
            {
                # Labs generally support clinical functions.
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 0.5,
            }
        ],

        "separation": [
            {
                # Conservative assumption:
                # Labs should not open directly into public zones.
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Labs are typically non-patient-facing.
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        # Labs are destinations, not connectors.
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
        ],
    },

    "optimization": {
        "centerBias": {
            # Bias toward clinical core, but weaker than sterilization.
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.4,
        },
    },
}

# Consult

CONSULT_RULES = {
    "identity": {
        "roomType": SPACE_ID.CONSULT,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": "Consult room used for patient discussions outside treatment spaces",
    },

    "existence": {
        # Explicit in rules:
        # Consult rooms are included only when requested by user input.
        "trigger": TRIGGER_ENUM.USER_INPUT,
        "countRules": [
            {
                # No deterministic scaling rules provided.
                # Quantity depends entirely on user request.
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": None,  # unbounded; controlled externally
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                # Ideal: same size as treatment room
                "label": "ideal_equals_treatment_room",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": None,    # TODO: resolved dynamically from treatment room model
                "lengthInches": None,   # TODO: resolved dynamically from treatment room model
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                # Minimum consult
                "label": "minimum_consult",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 96,      # 8'-0"
                "lengthInches": 96,     # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                # Living room consult
                "label": "living_room_consult",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 156,     # 13'-0"
                "lengthInches": 120,    # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        # Explicitly stated: no orientation rules for any layout
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # One entry required
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            },
            {
                # Second entry preferred if from clinical crossover hallway
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            },
        ],

        "entryConstraints": [
            {
                # Required: entry near check-out
                "kind": ENTRY_RULE_ENUM.ENTRY_NEAR,
                "target": SPACE_ID.CHECK_OUT,
                "distanceMaxInches": None,  # TODO: define "near" threshold if standardized
                "hard": True,
            },
            {
                # Preferred: entry near clinical hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_NEAR,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": False,
            },
            {
                # Optional second entry from crossover hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],

        "ada": {
            # Explicitly stated
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            # Explicitly none
        ],

        "preferredProximity": [
            {
                # Check-out within 15 feet
                "target": SPACE_ID.CHECK_OUT,
                "maxDistanceInches": 180,  # 15 ft
                "optimizationWeight": 1.0,
            }
        ],

        "separation": [
            {
                "target": SPACE_ID.MECHANICAL,
                "hard": True,
            },
            {
                "target": SPACE_ID.LAB,
                "hard": True,
            },
        ],
    },

    "visibility": {
        # Explicitly none
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        # Consult rooms are destinations accessed by patients.
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.PUBLIC,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "centerBias": {
            # Bias toward public / front-of-house zones
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Patient Restroom

PATIENT_RESTROOM_RULES = {
    "identity": {
        "roomType": SPACE_ID.PATIENT_RESTROOM,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": "Patient-facing restroom accessible from public circulation",
    },

    "existence": {
        # Explicit: included when noted by user input
        "trigger": TRIGGER_ENUM.USER_INPUT,

        "countRules": [
            {
                # 1 required if total square footage < 1500
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: encode threshold logic (<1500)
            },
            {
                # 2 required if square footage > 1500
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": 2,
                "max": 2,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: encode threshold logic (>1500)
            },
            {
                # 3 required if occupancy > 50
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": 3,
                "max": 3,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: encode threshold logic (>50)
            },
            {
                # +1 for every additional 50 occupants
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: encode incremental rule (per +50)
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                "label": "minimum_patient_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 99,   # 8'-3"
                "lengthInches": 93,  # 7'-9"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            }
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        # Explicitly no orientation constraints in any layout
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": None,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # One entry required
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],

        "entryConstraints": [
            {
                # Must not be accessed from within another room
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PRIVATE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Ideally not located directly in the patient lounge
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],

        "ada": {
            # Explicit ADA requirement
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            # None specified
        ],

        "preferredProximity": [
            {
                # Check-out should be within 15 feet
                "target": SPACE_ID.CHECK_OUT,
                "maxDistanceInches": 180,  # 15 ft
                "optimizationWeight": 0.8,
            }
        ],

        "separation": [
            # None specified
        ],
    },

    "visibility": {
        # Explicitly none
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        # Patient restrooms are destinations accessed from public circulation
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.PUBLIC,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "centerBias": {
            # Mild bias toward public/check-out zones
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.5,
        },
    },
}

# Treatment Coordination Station

TREATMENT_COORDINATION_RULES = {
    "identity": {
        "roomType": SPACE_ID.TREATMENT_COORDINATION,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Open clinical workstation supporting treatment operations",
    },

    "existence": {
        # Explicit: included only when requested
        "trigger": TRIGGER_ENUM.USER_INPUT,

        "countRules": [
            {
                # One coordinator per 10 operatories
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.PER_N_UNITS,  # TODO: encode divisor = 10
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                # One-person station
                "label": "one_person_station",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 10,
                "widthInches": 42,   # 3'-6"
                "lengthInches": 54,  # 4'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                # Two-person station
                "label": "two_person_station",
                "treatmentRoomsMin": 11,
                "treatmentRoomsMax": None,
                "widthInches": 42,   # 3'-6"
                "lengthInches": 90,  # 7'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        # All layouts: parallel to the long axis of the clinical hallway
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.ALONG,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.ALONG,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.ALONG,
            "connectsCorridors": True,
        },
    },

    "access": {
        # This is not a room with discrete doors
        # Modeled as zero formal entries, but continuous access
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 0,
                "maxEntries": 0,
            }
        ],

        "entryConstraints": [
            {
                # Entire length must be accessible from clinical hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Ideally not within 36" of crossover hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": 36,
                "hard": False,
            },
        ],

        # ADA modeled implicitly via corridor standards
        "ada": {
            "minClearWidthInches": None,  # TODO: relies on corridor ADA enforcement
            "requiredEntries": 0,
        },
    },

    "adjacency": {
        "direct": [
            # None specified
        ],

        "preferredProximity": [
            {
                # As close to center of treatment space as possible
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 1.0,
            }
        ],

        "separation": [
            {
                # Ideally not adjacent to patient restroom
                "target": SPACE_ID.PATIENT_RESTROOM,
                "hard": False,
            }
        ],
    },

    "visibility": {
        # No explicit visibility requirements
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        # Behaves as part of the clinical spine, not a destination
        "role": CIRCULATION_ROLE_ENUM.CONNECTOR,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
        ],
    },

    "optimization": {
        "centerBias": {
            # Strong bias toward clinical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}
