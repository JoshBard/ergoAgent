"""
room_rules.py

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

from .core import *
from .room_schema import RoomSchema


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

# Mobile Tech Area

MOBILE_TECH_RULES = {
    "identity": {
        "roomType": SPACE_ID.MOBILE_TECH,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Distributed mobile technology support area within clinical zones",
    },

    "existence": {
        # Always required
        "trigger": TRIGGER_ENUM.ALWAYS,

        "countRules": [
            {
                # One Mobile Tech area per clinical cluster of 5–8 treatment rooms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.PER_N_UNITS,  # TODO: encode cluster size = 5–8
            },
            {
                # Larger offices (10+ treatment rooms) may require multiple pods
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 10,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define distribution logic
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                "label": "standard_mobile_tech",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 42,   # 3'-6"
                "lengthInches": 84,  # 7'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            }
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        # All layouts: parallel to clinical hallway
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
        # Linear / open access, not discrete door-based
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
                # Must be accessible from clinical hallway or sterilization corridor
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": False,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.STERILIZATION,
                "distanceMaxInches": None,
                "hard": False,
            },
            {
                # Must not open directly into crossover hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
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

        # ADA compliance handled at corridor level
        "ada": {
            "minClearWidthInches": None,  # TODO: enforced via corridor rules
            "requiredEntries": 0,
        },
    },

    "adjacency": {
        "direct": [
            # None specified
        ],

        "preferredProximity": [
            {
                # As close to center of clinical (treatment room) space as possible
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 1.0,
            }
        ],

        "separation": [
            {
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                # Reception / check-in modeled as patient-facing
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Should not be visible from patient-facing zones
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": False,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        # Functions as a clinical support element along circulation
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
            # Bias toward clinical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.8,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Doctors On Deck

DOCTORS_ON_DECK_RULES = {
    "identity": {
        "roomType": SPACE_ID.DOCTORS_ON_DECK,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Doctor work nooks positioned along the clinical hallway for oversight and rapid response",
    },

    "existence": {
        # Conditionally required
        "trigger": TRIGGER_ENUM.DERIVED,

        "countRules": [
            {
                # Always required if >5 treatment rooms AND no doctor office on clinical floor
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 6,
                "max": None,
                "condition": CONDITION_ENUM.IF_ABSENT,  # TODO: absence of DOCTOR_OFFICE on clinical floor
            },
            {
                # 1 single-doctor nook for every 3–5 treatment rooms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 3,
                "max": 5,
                "condition": CONDITION_ENUM.PER_N_UNITS,  # TODO: encode 3–5 scaling window
            },
            {
                # Dual-doctor nook for 7–10 treatment rooms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 7,
                "max": 10,
                "condition": CONDITION_ENUM.IF_THRESHOLD,
            },
            {
                # Larger offices may require multiple nooks
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 7,
                "max": None,
                "condition": CONDITION_ENUM.PER_N_UNITS,  # TODO: multi-nook distribution logic
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                "label": "single_doctor_nook",
                "treatmentRoomsMin": 3,
                "treatmentRoomsMax": 5,
                "widthInches": 66,   # 5'-6"
                "lengthInches": 90,  # 7'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dual_doctor_nook_back_to_back",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": 10,
                "widthInches": 66,   # 5'-6"
                "lengthInches": 114, # 9'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dual_doctor_nook_side_by_side",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 90,   # 7'-6"
                "lengthInches": 102, # 8'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        # All layouts: positioned along clinical hallway
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
                # Must enter directly from clinical hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should not open directly into patient lounge
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should not open directly into reception / check-in
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,
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

        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
            # TODO: push/pull clearances, turning circle semantics
        },
    },

    "adjacency": {
        "direct": [
            {
                # Must connect directly to clinical hallway
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": None,
                "hard": True,
            }
        ],

        "preferredProximity": [
            {
                # Ideally central to treatment rooms
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 1.0,
            },
            {
                # Near consult rooms for quick transitions
                "target": SPACE_ID.CONSULT,
                "maxDistanceInches": None,
                "optimizationWeight": 0.6,
            },
        ],

        "separation": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeVisibleFrom": [
            {
                # Visibility into clinical hallway for quick response
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": False,
            }
        ],
        "mustBeHiddenFrom": [
            {
                # Should not be visible from patient-facing zones
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": False,
            }
        ],
    },

    "circulation": {
        # Active oversight node along circulation spine
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
            # Bias toward clinical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Doctor Office

DOCTOR_OFFICE_RULES = {
    "identity": {
        "roomType": SPACE_ID.DOCTOR_OFFICE,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": "Private or shared doctor office supporting focused work with proximity to treatment and consult spaces",
    },

    "existence": {
        # Exists only when explicitly requested
        "trigger": TRIGGER_ENUM.USER_INPUT,

        "countRules": [
            {
                # 1 private office for 1–5 treatment rooms if no Doctor’s Nook
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 5,
                "condition": CONDITION_ENUM.IF_ABSENT,  # TODO: absence of DOCTOR_NOOK
            },
            {
                # Shared office appropriate for 5–10 treatment rooms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 5,
                "max": 10,
                "condition": CONDITION_ENUM.IF_PRESENT,  # TODO: shared workspace requested
            },
            {
                # Larger practices may require both shared office + nooks
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 10,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,

        "dimensionModels": [
            {
                "label": "single_doctor_office",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 5,
                "widthInches": 96,   # 8'-0"
                "lengthInches": 96,  # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "shared_office_2_to_3_doctors",
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": 10,
                "widthInches": 120,  # 10'-0"
                "lengthInches": 156, # 13'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                # Length scales by doctor count
                "label": "shared_office_3_plus_doctors",
                "treatmentRoomsMin": 10,
                "treatmentRoomsMax": None,
                "widthInches": 90,   # 7'-6" depth
                "lengthInches": None,  # TODO: 5'-0" per doctor
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 60,  # TODO: interpret as per-doctor increment
            },
            {
                # Optional attached private restroom
                "label": "attached_private_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 60,   # 5'-0"
                "lengthInches": 60,  # 5'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
                # TODO: represent attachment relationship explicitly
            },
        ],

        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.ALONG,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.ALONG,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": True,  # via second crossover hallway
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
                # Default: entry from clinical hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": False,  # overridden in H-layout case
            },
            {
                # H-layout alternative: entry from second crossover hallway
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": None,
                "hard": False,  # TODO: distinguish primary vs secondary crossover
            },
            {
                # Must not open into patient lounge
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Must not open into reception / check-in
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,
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

        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Clinical hallway OR second crossover hallway
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": None,
                "hard": False,
            },
            {
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "condition": CONDITION_ENUM.IF_LAYOUT,  # H layout
                "hard": False,
            },
            {
                # Optional attached private restroom
                "target": SPACE_ID.DOCTOR_PRIVATE_RESTROOM,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": False,
            },
        ],

        "preferredProximity": [
            {
                # Near treatment rooms
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 0.8,
            },
            {
                # Near consult rooms
                "target": SPACE_ID.CONSULT,
                "maxDistanceInches": None,
                "optimizationWeight": 0.6,
            },
        ],

        "separation": [
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "visibility": {
        # No explicit visibility requirements
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
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
            # Bias toward clinical core but less than Doctors-on-Deck
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.6,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.5,
        },
    },
}

# Doctor Private Restroom

DOCTOR_PRIVATE_RESTROOM_RULES = {
    "identity": {
        "roomType": SPACE_ID.DOCTOR_PRIVATE_RESTROOM,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": "Private restroom accessible only from the associated doctor's office",
    },

    "existence": {
        # Only exists if doctor office exists
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.IF_PRESENT,  # present only if doctor office exists
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "default_private_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 60,   # 5'-0"
                "lengthInches": 60,  # 5'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,  # TODO: may vary depending on office
            "placementHint": PLACEMENT_ENUM.BETWEEN,          # attached to doctor office
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
                # Only accessible from doctor office
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.DOCTOR_OFFICE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should not be accessible from any public spaces
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,
                "distanceMaxInches": None,
                "hard": True,
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
                "target": SPACE_ID.DOCTOR_OFFICE,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": True,
            },
        ],

        "preferredProximity": [
            {
                "target": SPACE_ID.DOCTOR_OFFICE,
                "maxDistanceInches": 0,
                "optimizationWeight": 1.0,
            },
        ],

        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
        ],
    },

    "visibility": {
        # Should not be visible from patient-facing areas
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            # Optional: visible from doctor office
            {
                "target": SPACE_ID.DOCTOR_OFFICE,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [SPACE_ID.DOCTOR_OFFICE],
        "mustNotTerminateInto": [SPACE_GROUP.PUBLIC, SPACE_GROUP.CLINICAL],
    },

    "optimization": {
        "centerBias": {
            "reference": None,  # TODO: could bias toward office cluster
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Office Manager

OFFICE_MANAGER_RULES = {
    "identity": {
        "roomType": SPACE_ID.OFFICE_MANAGER,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": "Office manager office located near reception and business offices, away from clinical zones",
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "min_office_manager",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 66,  # 5'-6"
                "lengthInches": 90, # 7'-6"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "max_office_manager",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 96,  # 8'-0"
                "lengthInches": 96, # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_NEAR,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": 120,  # 10 ft
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_RESTROOM,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],  # None required
        "preferredProximity": [
            {
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": None,  # TODO: exact preferred distance
                "optimizationWeight": 1.0,
            },
            {
                "target": SPACE_GROUP.SUPPORT,  # for business offices nearby
                "maxDistanceInches": None,
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [SPACE_GROUP.PUBLIC],
        "mustNotTerminateInto": [SPACE_GROUP.CLINICAL],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Business Office

BUSINESS_OFFICE_RULES = {
    "identity": {
        "roomType": SPACE_ID.BUSINESS_OFFICE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": "Administrative office located behind reception/check-in or check-out, supports business operations",
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,  # Only exists in practices with more than 4 treatment rooms
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: specify exact threshold for inclusion
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small",
                "treatmentRoomsMin": 0,
                "treatmentRoomsMax": 6,
                "widthInches": 90,   # 7'-6"
                "lengthInches": 96,  # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "medium",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": 10,
                "widthInches": 114,  # 9'-6"
                "lengthInches": 96,  # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large",
                "treatmentRoomsMin": 11,
                "treatmentRoomsMax": 15,
                "widthInches": 114,  # 9'-6"
                "lengthInches": 144, # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 0,
                "treatmentRoomsMax": 6,
                "minEntries": 1,
                "maxEntries": 1,
            },
            {
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": 15,
                "minEntries": 1,
                "maxEntries": 2,
            },
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NEAR,
                "target": SPACE_ID.CHECK_IN,
                "distanceMaxInches": 120,  # ~10 ft
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": 36,
                "hard": True,
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
                "target": SPACE_ID.CHECK_IN,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
            {
                "target": SPACE_ID.CHECK_OUT,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.OFFICE_MANAGER,
                "maxDistanceInches": None,  # TODO: exact preferred distance
                "optimizationWeight": 1.0,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_RESTROOM,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": False,
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [SPACE_ID.CHECK_IN, SPACE_ID.CHECK_IN],
        "mustNotTerminateInto": [SPACE_GROUP.CLINICAL],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Alt Business Office

ALT_BUSINESS_OFFICE_RULES = {
    "identity": {
        "roomType": SPACE_ID.ALT_BUSINESS_OFFICE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Alternate business office model sized by workstation capacity "
            "rather than fixed room dimensions; supports scalable admin teams"
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_GREATER_THAN,
                "threshold": 4,
            },
        ],
    },

    "capacity": {#this block isn't part of schema but relevant to this room so idk
        "workstations": {
            "min": 2,
            "perTreatmentRooms": 2,   # 1 workstation per 2 treatment rooms
            "rounding": ROUNDING_ENUM.CEIL,
        },
        "areaPerWorkstation": {
            "minNSF": 40,
            "maxNSF": 60,
            "defaultNSF": 50,
        },
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small",
                "treatmentRoomsMin": 0,
                "treatmentRoomsMax": 6,
                "workstationsMin": 2,
                "workstationsMax": 3,
                "areaSqFtMin": 80,
                "areaSqFtMax": 180,
                "aspectRatioRange": (1.2, 2.5),
            },
            {
                "label": "medium",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": 12,
                "workstationsMin": 4,
                "workstationsMax": 6,
                "areaSqFtMin": 160,
                "areaSqFtMax": 360,
                "aspectRatioRange": (1.2, 3.0),
            },
            {
                "label": "large",
                "treatmentRoomsMin": 13,
                "treatmentRoomsMax": None,
                "workstationsMin": 7,
                "workstationsMax": None,
                "areaSqFtMin": 400,
                "areaSqFtMax": None,
                "aspectRatioRange": (1.5, 4.0),
                "notes": "Expand into dedicated business area or command center",
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.AREA_FIRST,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.BEHIND_RECEPTION,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.BEHIND_OR_ADJACENT_TO_CHECKOUT,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.BUSINESS_ANCHOR,
            "pairWith": SPACE_ID.OFFICE_MANAGER,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "workstationsMin": 2,
                "workstationsMax": 3,
                "minEntries": 1,
                "maxEntries": 1,
            },
            {
                "workstationsMin": 4,
                "workstationsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            },
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NEAR,
                "target": SPACE_GROUP.FRONT_OF_HOUSE,
                "distanceMaxInches": 120,  # 10 ft
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.SECONDARY_ENTRY_ALLOWED_TO,
                "target": SPACE_ID.OFFICE_MANAGER,
                "hard": False,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "distanceMaxInches": 36,
                "hard": True,
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
                "target": SPACE_ID.CHECK_IN,
                "hard": False,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": False,
            },
            {
                "target": SPACE_ID.CHECK_OUT,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.OFFICE_MANAGER,
                "optimizationWeight": 1.0,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_RESTROOM,
                "hard": True,
            },
            {
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": False,
            },
        ],
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [SPACE_GROUP.FRONT_OF_HOUSE],
        "mustNotTerminateInto": [SPACE_GROUP.CLINICAL],
    },

    "optimization": {
        "compactnessBias": {
            "weight": 0.6,
        },
        "adjacencyClusterBias": {
            "targetGroup": SPACE_GROUP.PRIVATE,
            "weight": 0.9,
        },
    },
}

# Staff Lounge

STAFF_LOUNGE_RULES = {
    "identity": {
        "roomType": SPACE_ID.STAFF_LOUNGE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Staff-only lounge providing seating, kitchenette, and lockers; "
            "capacity and area scale linearly with treatment room count."
        ),
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

    "capacity": { #again, geometry for room derived from capacity
        # Seating
        "seating": {
            "seatsPerTreatmentRooms": 7 / 5,  # ~7 seats per 5 treatment rooms
            "rounding": ROUNDING_ENUM.CEIL,
            "areaPerSeatNSF": 20,
        },

        # Kitchenette
        "kitchenette": {
            "linearFeetPerSeat": {
                "min": 1.0,
                "max": 1.2,
            },
            "minLinearFeet": 8,
            "areaPerLinearFootSF": 5.5,  # includes counter depth + working aisle
        },

        # Lockers
        "lockers": {
            "lockersPerStaff": 1,  # TODO: define staff count derivation
            "lockersPerLinearFootMin": 1,
            "lockersPerLinearFootMax": 3,
            "areaPerLinearFootSF": 5.0,  # locker depth + aisle
            # TODO: clarify staff-to-treatment-room ratio
        },
    },

    # Geometry Envelope (Derived from Capacity)

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "capacity_driven",
                "derivation": "seating + kitchenette + lockers",
                "aspectRatioRange": (1.2, 3.5),
                # TODO: define preferred min/max depths for daylight walls
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.BACK,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.BACK,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.END,
            "anchorsStaffSpine": True,
            "preferExteriorWall": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "seatsMin": 0,
                "seatsMax": 10,
                "minEntries": 1,
                "maxEntries": 1,
            },
            {
                "seatsMin": 11,
                "seatsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            },
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.STAFF,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                "target": SPACE_ID.STAFF_ENTRY,
                "optimizationWeight": 0.8,
            },
            {
                "target": SPACE_ID.STAFF_RESTROOMS,
                "optimizationWeight": 0.9,
            },
        ],
        "separation": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            },
        ],
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
        "mustConnect": [SPACE_GROUP.STAFF],
        "mustNotTerminateInto": [SPACE_GROUP.PATIENT_FACING],
    },

    "optimization": {
        "daylightBias": {
            "preferred": True,
            "weight": 0.6,
        },
        "staffClusterBias": {
            "weight": 0.8,
        },
    },
}

# Patient Lounge

PATIENT_LOUNGE_RULES = {
    "identity": {
        "roomType": SPACE_ID.PATIENT_LOUNGE,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Primary patient waiting lounge providing seating, refreshment area, "
            "and optional integration with check-in and check-out zones."
        ),
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

    "capacity": {
        # Seating
        "seating": {
            "seatsPerTreatmentRoom": 1.5,
            "rounding": ROUNDING_ENUM.CEIL,
            "areaPerSeatNSF": 20,
        },

        # Refreshment Counter
        "refreshment": {
            "linearFeetMin": 4,
            "linearFeetMax": 6,
            "areaPerLinearFootSF": 5.5,
        },

        # Integrated Front-of-House Zones
        "frontOfHouseIntegration": {
            "checkInAdjacencyAreaNSF": {
                "min": 30,
                "max": 50,
            },
            "checkOutAdjacencyAreaNSF": {
                "min": 30,
                "max": 50,
            },
            # TODO: clarify if these are additive or mutually exclusive
        },
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "capacity_driven_lounge",
                "derivation": "seating + refreshment + front_of_house_buffers",
                "allowsClusteredSeating": True,
                "aspectRatioRange": (1.1, 3.0),
                # TODO: define preferred minimum depth for waiting furniture
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "anchorsFrontBand": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsEntry": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
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
                "target": SPACE_ID.CHECK_IN,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.PATIENT_RESTROOM,
                "maxDistanceInches": 240,  # 20 ft
                "optimizationWeight": 0.9,
            }
        ],
        "separation": [
            {
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
            },
            {
                "target": SPACE_ID.LAB,
                "hard": True,
            },
            {
                "target": SPACE_ID.MECHANICAL,
                "hard": True,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            }
        ],
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CHECK_IN,
            SPACE_GROUP.PUBLIC,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "entryVisibilityBias": {
            "weight": 0.9,
        },
        "noiseSeparationBias": {
            "fromClinical": True,
            "weight": 0.8,
        },
        "familyZoningBias": {
            "enableWhenTreatmentRoomsGTE": 15,
            "weight": 0.6,
            # TODO: define zoning semantics (play area, quiet area)
        },
    },
}

# Crossover Hallway

CROSSOVER_HALLWAY_RULES = {
    "identity": {
        "roomType": SPACE_ID.CROSSOVER_HALLWAY,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Connector corridor linking parallel clinical hallways. "
            "Functions strictly as a crossover, not as a primary circulation spine."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.IF_LAYOUT,  # parallel clinical corridors
                # TODO: encode explicit condition parameters (parallel corridors present)
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_crossover",
                "widthInches": 60,  # 5'-0" minimum
                "widthPreferredMaxInches": 72,  # 6'-0" preferred
                "lengthStrategy": "minimize",
                "highTrafficThresholdTreatmentRooms": 10,
                # TODO: formalize length minimization heuristic
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "minEntries": 2,
                "maxEntries": 2,
                # one into each parallel clinical corridor
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 60,
            "requiredEntries": 2,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [],
        "separation": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            },
            {
                "target": SPACE_ID.CHECK_OUT,
                "hard": True,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
                # specifically dirty side – TODO: dirty/clean sub-zoning
            },
            {
                "target": SPACE_ID.TREATMENT_ROOM,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_RESTROOM,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.CONNECTOR,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
            SPACE_GROUP.PATIENT_FACING,
        ],
    },

    "optimization": {
        "lengthMinimizationBias": {
            "weight": 1.0,
        },
        "evenDistributionBias": {
            "reference": SPACE_ID.CLINICAL_CORRIDOR,
            "intervalInches": 720,  # 60 ft
            "weight": 0.8,
        },
        "patientExposureMinimization": {
            "weight": 0.9,
        },
        # TODO: differentiate Primary vs Secondary crossover types
    },
}

# Clinical Corridor

CLINICAL_CORRIDOR_RULES = {
    "identity": {
        "roomType": SPACE_ID.CLINICAL_CORRIDOR,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Primary clinical circulation spine providing access to treatment rooms "
            "and support spaces. Organizes clinical flow and connects via crossover hallways."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.IF_PRESENT,
                # Always required when treatment rooms exist
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "clinical_corridor_standard",
                "widthInches": 60,              # 5'-0" minimum clear
                "widthPreferredMaxInches": 72,  # 6'-0" preferred max
                "lengthStrategy": "scale_with_treatment_rooms",
                # TODO: formalize LF per treatment room coefficient
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.ALONG,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.ALONG,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.ALONG,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "minEntries": 1,
                "maxEntries": None,
                # corridor is continuous; entries handled by connected spaces
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.TREATMENT_ROOM,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.DOCTORS_ON_DECK,
                "hard": False,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.MOBILE_TECH,
                "hard": False,
            },
        ],
        "ada": {
            "minClearWidthInches": 60,
            "requiredEntries": 1,
            # TODO: encode passing space / turning radius intervals if needed
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.TREATMENT_ROOM,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
            {
                "target": SPACE_ID.STERILIZATION,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
            {
                "target": SPACE_ID.MOBILE_TECH,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
            {
                "target": SPACE_ID.DOCTORS_ON_DECK,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
            {
                "target": SPACE_ID.CROSSOVER_HALLWAY,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.CONSULT,
                "maxDistanceInches": None,
                "optimizationWeight": 0.6,
            },
            {
                "target": SPACE_ID.PATIENT_RESTROOM,
                "maxDistanceInches": None,
                "optimizationWeight": 0.6,
            },
        ],
        "separation": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.LAB,
                "hard": False,
            },
            {
                "target": SPACE_ID.MECHANICAL,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
        # NOTE: wayfinding treated as optimization, not hard visibility
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.SPINE,
        "mustConnect": [
            SPACE_ID.TREATMENT_ROOM,
            SPACE_ID.STERILIZATION,
            SPACE_ID.CROSSOVER_HALLWAY,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
            SPACE_GROUP.PATIENT_FACING,
        ],
    },

    "optimization": {
        "continuityBias": {
            "weight": 1.0,  # discourage breaks or dead-ends
        },
        "evenTreatmentDistributionBias": {
            "reference": SPACE_ID.TREATMENT_ROOM,
            "weight": 0.8,
        },
        "crossoverSpacingBias": {
            "intervalInches": 720,  # 60 ft
            "weight": 0.9,
        },
        "wayfindingClarityBias": {
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.5,
        },
        # TODO: formalize signage / visual cues if needed later
    },
}

# Treatment Room

TREATMENT_ROOM_RULES = {
    "identity": {
        "roomType": SPACE_ID.TREATMENT_ROOM,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "General practice treatment room with standardized chair orientation "
            "and configurable entry strategies (dual-entry, side-toe entry, toe entry)."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.USER_INPUT,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.IF_PRESENT,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "widthRules": {
            "minInches": 97,     # 8'-1"
            "idealInches": 100,  # 8'-4"
            "maxInches": 108,    # 9'-0"
        },
        "depthRules": {
            "dualEntryMinInches": 126,     # 10'-6"
            "sideToeEntryMinInches": 132,  # 11'-0"
            "toeEntryMinInches": 132,      # 11'-0"
        },
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.IDEAL_THEN_MIN,
    },

    "chairOrientation": {       #this field only exists for treatment room, could be done better or ignored?
        "longAxis": {
            "from": CLOCK_FACE_ENUM.TWELVE_OCLOCK,  # headwall
            "to": CLOCK_FACE_ENUM.SIX_OCLOCK,        # toe wall
        },
        "wallDefinitions": {
            "headwall": CLOCK_FACE_ENUM.TWELVE_OCLOCK,
            "toewall": CLOCK_FACE_ENUM.SIX_OCLOCK,
            "rightWall": CLOCK_FACE_ENUM.THREE_OCLOCK,
            "leftWall": CLOCK_FACE_ENUM.NINE_OCLOCK,
        },
        "chairCentered": True,
    },

    "entryVariants": {      #this field also only exists for this room type
        "dual_entry": {
            "definition": (
                "Two doorless framed openings on the headwall, "
                "straddling the chair head for bilateral circulation."
            ),
            "depthRequirementInches": 126,  # 10'-6"
            "entries": [
                {
                    "wall": CLOCK_FACE_ENUM.TWELVE_OCLOCK,
                    "side": CLOCK_FACE_ENUM.NINE_OCLOCK,
                    "clearWidthInches": 36,
                    #"doorType": DOOR_TYPE_ENUM.OPENING,
                    "hard": True,
                },
                {
                    "wall": CLOCK_FACE_ENUM.TWELVE_OCLOCK,
                    "side": CLOCK_FACE_ENUM.THREE_OCLOCK,
                    "clearWidthInches": {
                        "min": 25,
                        "typical": 28,
                        "max": 36,
                    },
                    #"doorType": DOOR_TYPE_ENUM.OPENING,
                    "hard": True,
                },
            ],
            "headwallClearance": {
                "minBetweenOpeningsInches": 36,
                "scalesWithRoomWidth": True,
            },
            "adjacency": {
                "mustConnectTo": [SPACE_ID.CLINICAL_CORRIDOR],
                "antiParallelRule": {
                    "target": SPACE_ID.TREATMENT_ROOM,
                    "condition": "not_directly_opposite",
                    "reason": "acoustic_control",
                },
            },
        },

        "side_toe_entry": {
            "definition": (
                "Single swing door on the side wall near the toe, "
                "used when room long axis runs parallel to corridor."
            ),
            "depthRequirementInches": 132,  # 11'-0"
            "entries": [
                {
                    "wall": [CLOCK_FACE_ENUM.THREE_OCLOCK, CLOCK_FACE_ENUM.NINE_OCLOCK],
                    "positionBias": CLOCK_FACE_ENUM.SIX_OCLOCK,
                    #"doorType": DOOR_TYPE_ENUM.SWING,
                    "hard": True,
                }
            ],
            "adjacency": {
                "mustConnectTo": [SPACE_ID.CLINICAL_CORRIDOR],
            },
        },

        "toe_entry": {
            "definition": (
                "Single swing door on the toe wall, offset from the chair centerline."
            ),
            "depthRequirementInches": 132,  # 11'-0"
            "entries": [
                {
                    "wall": CLOCK_FACE_ENUM.SIX_OCLOCK,
                    #"alignment": ALIGNMENT_ENUM.OFF_CENTER,
                    "offsetToward": [
                        CLOCK_FACE_ENUM.THREE_OCLOCK,
                        CLOCK_FACE_ENUM.NINE_OCLOCK,
                    ],
                    #"doorType": DOOR_TYPE_ENUM.SWING,
                    "hard": True,
                }
            ],
            "constraints": {
                #"forbiddenAlignment": ALIGNMENT_ENUM.CENTERLINE,
            },
            "adjacency": {
                "mustConnectTo": [SPACE_ID.CLINICAL_CORRIDOR],
            },
        },
    },

    "orientation": {
        "longAxisRelationToCorridor": {
            "dual_entry": AXIS_RELATION_ENUM.PERPENDICULAR,
            "side_toe_entry": AXIS_RELATION_ENUM.PARALLEL,
            "toe_entry": AXIS_RELATION_ENUM.PERPENDICULAR,
        }
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            }
        ],
        "acousticControls": {
            "avoidDirectOpposition": True,
        },
    },
}
