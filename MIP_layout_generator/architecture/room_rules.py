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
            # {
            #     # Optional attached private restroom
            #     "label": "attached_private_restroom",
            #     "treatmentRoomsMin": None,
            #     "treatmentRoomsMax": None,
            #     "widthInches": 60,   # 5'-0"
            #     "lengthInches": 60,  # 5'-0"
            #     "areaSqIn": None,
            #     "longAxisVariable": False,
            #     "longAxisIncrementPerDoorInches": None,
            #     # TODO: represent attachment relationship explicitly
            # },
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
                "target": SPACE_ID.STAFF_RESTROOM,
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

# Check In

CHECK_IN_RULES = {

    "identity": {
        "roomType": SPACE_ID.CHECK_IN,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Primary patient arrival and intake space for greeting, "
            "registration, and wayfinding."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.ALWAYS,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_desk",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 96,
                "lengthInches": 84,
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dual_desk",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 120,
                "lengthInches": 96,
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
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.ENTRY,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": None,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.BUSINESS_OFFICE,
                "maxDistanceInches": 120,
                "optimizationWeight": 1.0,
            }
        ],
        "separation": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.FRONT_OF_HOUSE,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.3,
        },
    },
}

# Check Out

CHECK_OUT_RULES = {

    "identity": {
        "roomType": SPACE_ID.CHECK_OUT,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Patient-facing departure area for billing, scheduling, "
            "and visit completion."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.ALWAYS,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_position",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 84,
                "lengthInches": 72,
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dual_position",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 120,
                "lengthInches": 84,
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
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.ENTRY,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": None,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.BUSINESS_OFFICE,
                "maxDistanceInches": 120,
                "optimizationWeight": 1.2,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.FRONT_OF_HOUSE,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.2,
        },
    },
}

# Mechanical

MECHANICAL_RULES = {

    "identity": {
        "roomType": SPACE_ID.MECHANICAL,
        "category": ROOM_CATEGORY.PRIVATE,  # back-of-house / support
        "description": (
            "Building mechanical and MEP service room housing HVAC, "
            "electrical panels, IT racks, and related infrastructure."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Base assumption: at least one mechanical room is required
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Larger buildings may require more than one
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": 2,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define sqft threshold
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_mechanical",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 120,  # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "medium_mechanical",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": 12,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 144,  # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_mechanical",
                "treatmentRoomsMin": 13,
                "treatmentRoomsMax": None,
                "widthInches": 144,   # 12'-0"
                "lengthInches": 180,  # 15'-0"
                "areaSqIn": None,
                "longAxisVariable": True,  # equipment-driven layouts
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.END,  # end of spine
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,  # secondary service access possible
            }
        ],
        "entryConstraints": [
            {
                # Should not be accessed from patient-facing areas
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,  # TODO: ensure this group exists
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Prefer staff or service corridor access
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.SUPPORT,  # TODO: define support circulation
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # Not a public-access space; allow narrower service door
            "minClearWidthInches": 32,  # TODO: confirm with code requirements
            "requiredEntries": 0,
        },
    },

    "adjacency": {
        "direct": [
            # No required direct adjacencies
        ],
        "preferredProximity": [
            {
                # Prefer proximity to lab / sterilization for MEP efficiency
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": None,
                "optimizationWeight": 0.4,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                "target": SPACE_ID.TREATMENT_ROOM,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.CONSULT,
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
        "mustBeVisibleFrom": [
            # None
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            # Staff / support corridor preferred but not mandatory
            # TODO: add STAFF_CORRIDOR enum if needed
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": None,  # no centrality preference
            "weight": 0.0,
        },
        "layoutCohesionBias": {
            # Encourage grouping with other support spaces
            "sameCategoryBonus": 0.6,
        },
    },
}

# Staff Restrooms

STAFF_RESTROOM_RULES = {

    "identity": {
        "roomType": SPACE_ID.STAFF_RESTROOM,
        "category": ROOM_CATEGORY.PRIVATE,  # staff-only support space
        "description": (
            "Staff-only restroom facilities intended for employees and providers. "
            "Separated from patient circulation and patient-facing zones."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Minimum one staff restroom in any staffed practice
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Additional restrooms as staff count / practice size increases
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 2,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define treatment room threshold
            },
            {
                # Occupancy-based scaling (code-driven)
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define occupancy thresholds
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_user_staff_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 8,
                "widthInches": 60,    # 5'-0"
                "lengthInches": 96,   # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "ada_staff_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 90,    # 7'-6"
                "lengthInches": 96,   # 8'-0"
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
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.END,
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
                # Must not be accessed from patient-facing zones
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,  # TODO: ensure group exists
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Preferred access from staff/support circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.SUPPORT,  # TODO: confirm support corridor grouping
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # At least one ADA-compliant staff restroom is typically required
            "minClearWidthInches": 34,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            # No required direct adjacencies
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "maxDistanceInches": None,
                "optimizationWeight": 0.6,
            },
            {
                "target": SPACE_ID.STAFF_ENTRY,
                "maxDistanceInches": None,
                "optimizationWeight": 0.4,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
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
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            # None
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            # TODO: add STAFF_CORRIDOR enum if explicitly modeled later
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            # No global centrality preference
            "reference": None,
            "weight": 0.0,
        },
        "layoutCohesionBias": {
            # Encourage grouping with staff support spaces
            "sameCategoryBonus": 0.7,
        },
    },
}

# Doctor Nook

DOCTOR_NOOK_RULES = {

    "identity": {
        "roomType": SPACE_ID.DOCTOR_NOOK,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "A small semi-private workspace for doctors/providers used for "
            "charting, brief consultations, phone calls, and case review. "
            "Not intended for patient occupancy."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # At least one nook in any provider-based practice
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Scale with number of treatment rooms / providers
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define scaling breakpoint
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_provider_nook",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 84,   # 7'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dual_provider_nook",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 96,   # 8'-0"
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
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": None,
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                # Should not be directly accessed from public/patient spaces
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Prefer access from clinical circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # Not a patient-occupied space; ADA may not strictly apply
            # TODO: confirm local code interpretation
            "minClearWidthInches": 32,
            "requiredEntries": 0,
        },
    },

    "adjacency": {
        "direct": [
            # No strictly required direct adjacencies
        ],
        "preferredProximity": [
            {
                # Close to treatment rooms for efficiency
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 0.8,
            },
            {
                "target": SPACE_ID.DOCTOR_PRIVATE_RESTROOM,
                "maxDistanceInches": None,
                "optimizationWeight": 0.4,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "maxDistanceInches": None,
                "optimizationWeight": 0.3,
            },
        ],
        "separation": [
            {
                # Avoid public-facing and waiting areas
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
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
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            # None required
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            # TODO: add explicit CLINICAL_CORRIDOR if modeled separately
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            # Mild pull toward clinical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            # Encourage grouping with other provider-only spaces
            "sameCategoryBonus": 0.6,
        },
    },
}

# Vestibule

VESTIBULE_RULES = {

    "identity": {
        "roomType": SPACE_ID.VESTIBULE,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Primary entry vestibule providing weather, acoustic, and thermal "
            "buffer between exterior building entry and interior public spaces. "
            "Functions as the first transition into the facility."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                # Typically one main vestibule per practice
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Optional additional vestibules for large practices or secondary entries
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,  # TODO: define sqft threshold
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_single_door_vestibule",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 8,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 96,   # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "double_door_or_high_traffic_vestibule",
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": None,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 120,  # 10'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Exterior entry + interior entry
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 2,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                # Must connect to exterior
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Must connect to public interior space
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Must not directly access clinical areas
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            # Vestibule is fully ADA-required
            "minClearWidthInches": 36,
            "requiredEntries": 2,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                # Reception should be immediately visible after vestibule
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.9,
            }
        ],
        "separation": [
            {
                # Strong separation from back-of-house
                "target": SPACE_GROUP.PRIVATE,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Vestibule should not expose clinical spaces
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                # Vestibule should be visible from reception for supervision
                "target": SPACE_ID.CHECK_IN,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.CONNECTOR,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
            SPACE_ID.STAFF_LOUNGE,
            SPACE_ID.STAFF_RESTROOM,
        ],
    },

    "optimization": {
        "centerBias": {
            # Vestibule should pull toward building front, not plan center
            "reference": SPACE_GROUP.PUBLIC,
            "weight": -0.5,
        },
        "layoutCohesionBias": {
            # Encourage grouping with other public spaces
            "sameCategoryBonus": 0.7,
        },
    },
}
# Children's Area

CHILDRENS_RULES = {

    "identity": {
        "roomType": SPACE_ID.CHILDRENS,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Dedicated children’s activity or play area intended for pediatric patients "
            "and siblings while waiting. Typically integrated into or directly adjacent "
            "to the main patient lounge and designed for visibility and supervision."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Typically provided only for family / pediatric practices
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 6,
                "max": None,
                "condition": CONDITION_ENUM.PER_N_UNITS,  # TODO: define trigger
            },
            {
                # Generally only one children’s area per practice
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_children_zone",
                "treatmentRoomsMin": 6,
                "treatmentRoomsMax": 10,
                "widthInches": 96,     # 8'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_children_zone",
                "treatmentRoomsMin": 11,
                "treatmentRoomsMax": None,
                "widthInches": 120,    # 10'-0"
                "lengthInches": 144,   # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Often open to lounge with no door, but modeled as one entry
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                # Must connect to patient lounge
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Must not connect directly to clinical areas
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            # Clear access path required, even if furniture-based
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                # Visibility from reception for supervision
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": 360,  # ~30'
                "optimizationWeight": 0.6,
            },
            {
                # Parents often need restrooms nearby
                "target": SPACE_ID.PATIENT_RESTROOM,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
            {
                "target": SPACE_ID.STAFF_LOUNGE,
                "hard": True,
            },
            {
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Children should not see clinical activity
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                # Passive supervision from lounge or reception
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": False,
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
    },

    "optimization": {
        "centerBias": {
            # Bias toward public front-of-house zones
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            # Strong cohesion with other public-facing spaces
            "sameCategoryBonus": 0.8,
        },
    },
}

# Refreshment Area

REFRESHMENT_RULES = {

    "identity": {
        "roomType": SPACE_ID.REFRESHMENT,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Small refreshment or beverage area intended for patient use. "
            "Typically includes a counter, beverage station, and light storage. "
            "Often integrated into or directly adjacent to the patient lounge."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Common in mid-size and larger practices
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 6,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Typically only one refreshment area
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "compact_refreshment",
                "treatmentRoomsMin": 6,
                "treatmentRoomsMax": 10,
                "widthInches": 60,     # 5'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "expanded_refreshment",
                "treatmentRoomsMin": 11,
                "treatmentRoomsMax": None,
                "widthInches": 72,     # 6'-0"
                "lengthInches": 120,   # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Often open to lounge, modeled as one access point
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.CHECK_OUT,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 0.6,
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
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                # Passive visibility from lounge
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Retail Area

RETAIL_RULES = {

    "identity": {
        "roomType": SPACE_ID.RETAIL,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Retail display area for dental products such as toothbrushes, "
            "whitening kits, or oral care accessories. Intended for patient "
            "browsing near check-out and reception zones."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 5,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Typically a single consolidated retail area
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        # Often wall-based or shallow footprint
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "wall_retail_zone",
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": None,
                "widthInches": 48,     # 4'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Often open-access with no door
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CHECK_OUT,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # Clear aisle in front of retail wall
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.CHECK_OUT,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.6,
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
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                # Encourages browsing near checkout
                "target": SPACE_ID.CHECK_OUT,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CHECK_OUT,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_ID.CHECK_OUT,
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Imaging Room

IMAGING_RULES = {

    "identity": {
        "roomType": SPACE_ID.IMAGING,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Dedicated diagnostic imaging room for radiographic equipment "
            "(e.g., panoramic, cephalometric, CBCT, or intraoral imaging support). "
            "Requires shielding and controlled access."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # One imaging room serves multiple operatories
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 4,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Usually single-room imaging
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 2,  # TODO: confirm if multiple imaging modalities are separated
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "intraoral_or_pano",
                "treatmentRoomsMin": 4,
                "treatmentRoomsMax": 8,
                "widthInches": 84,     # 7'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "cbct_capable",
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": None,
                "widthInches": 96,     # 8'-0"
                "lengthInches": 120,   # 10'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PERPENDICULAR,
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
                # Must be accessed from clinical circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                # Imaging should be near treatment rooms
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                # Keep imaging away from public spaces
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.CLINICAL,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.6,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Photo Room

PHOTO_RULES = {

    "identity": {
        "roomType": SPACE_ID.PHOTO,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Room dedicated to patient photography such as smile photos, "
            "before/after documentation, or orthodontic records. "
            "Requires controlled lighting and privacy."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Often present in ortho / cosmetic practices
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 6,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Usually single room
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_photo",
                "treatmentRoomsMin": 6,
                "treatmentRoomsMax": None,
                "widthInches": 72,     # 6'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                # Often paired with imaging or consult
                "target": SPACE_ID.IMAGING,
                "maxDistanceInches": 180,  # ~15'
                "optimizationWeight": 0.6,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.CLINICAL,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.PUBLIC,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Multi Stall Restroom

MULTI_STALLS_RULES = {

    "identity": {
        "roomType": SPACE_ID.MULTI_STALLS,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Public multi-stall restroom intended for patient and visitor use. "
            "Includes multiple toilet compartments and shared lavatory area. "
            "Must comply with ADA accessibility and plumbing code requirements."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Multi-stall restrooms appear once patient volume exceeds a threshold
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 8,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Typically one multi-stall restroom per clinic
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 2,  # TODO: confirm if gender-separated or duplicated per wing
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "two_to_three_stalls",
                "treatmentRoomsMin": 8,
                "treatmentRoomsMax": 14,
                "widthInches": 96,     # 8'-0"
                "lengthInches": 144,   # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,  # additional stall
            },
            {
                "label": "four_plus_stalls",
                "treatmentRoomsMin": 15,
                "treatmentRoomsMax": None,
                "widthInches": 120,    # 10'-0"
                "lengthInches": 168,   # 14'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.EXPAND_LONG_AXIS,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
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
                # Must be accessed from public circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Avoid direct exposure to waiting areas
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_ID.PATIENT_LOUNGE,
                "distanceMaxInches": 120,
                "hard": False,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                # Should be near waiting / reception
                "target": SPACE_GROUP.PUBLIC,
                "maxDistanceInches": 300,  # ~25'
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                # Should not open directly into clinical rooms
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            },
            {
                # Avoid adjacency to sterilization or lab
                "target": SPACE_ID.STERILIZATION,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Restroom interiors must not be visible from public spaces
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
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
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Toy Room

TOY_RULES = {

    "identity": {
        "roomType": SPACE_ID.TOY,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Toy or play room intended for children in pediatric or family-oriented clinics. "
            "Provides a safe, supervised play environment, typically adjacent to waiting or "
            "children's areas."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Only needed if clinic serves children
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 4,
                "max": None,
                "condition": CONDITION_ENUM.IF_PRESENT,  # TODO: confirm pediatric flag logic
            },
            {
                # Usually a single shared toy room
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "toy_alcove",
                "treatmentRoomsMin": 4,
                "treatmentRoomsMax": 8,
                "widthInches": 72,     # 6'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "dedicated_play_room",
                "treatmentRoomsMin": 9,
                "treatmentRoomsMax": None,
                "widthInches": 120,    # 10'-0"
                "lengthInches": 144,   # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.FRONT,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.FRONT,
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
                # Must be accessed from a public or waiting area
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should avoid direct adjacency to clinical rooms
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_WITHIN_DISTANCE,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": 120,
                "hard": False,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Commonly adjacent to children’s waiting
                "target": SPACE_ID.CHILDRENS,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                # Should be near waiting for supervision
                "target": SPACE_ID.PATIENT_LOUNGE,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 0.9,
            },
        ],
        "separation": [
            {
                # Should not be adjacent to imaging or lab
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [
            {
                # Prefer line-of-sight from waiting / reception
                "target": SPACE_ID.PATIENT_LOUNGE,
                "hard": False,
            },
        ],
    },

    "circulation": {
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
            "reference": SPACE_ID.PATIENT_LOUNGE,
            "weight": 0.8,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Universal Room

UNIVERSAL_RULES = {

    "identity": {
        "roomType": SPACE_ID.UNIVERSAL,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Flexible, multi-purpose room intended to support changing clinical, consult, "
            "education, or overflow needs. Designed to be adaptable over time rather than "
            "dedicated to a single function."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Optional but common in medium+ clinics
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 6,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Typically limited in number
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 2,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_universal",
                "treatmentRoomsMin": 6,
                "treatmentRoomsMax": 9,
                "widthInches": 108,   # 9'-0"
                "lengthInches": 120,  # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "standard_universal",
                "treatmentRoomsMin": 10,
                "treatmentRoomsMax": None,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 144,  # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                # Must connect to clinical circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Always clinical-facing
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                # Useful near consult or imaging
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.6,
            },
        ],
        "separation": [
            {
                # Avoid public-facing adjacency due to variable use
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Avoid exposure to waiting / reception
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            },
        ],
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
            # Slight bias toward clinical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Hygiene Room

HYGIENE_RULES = {

    "identity": {
        "roomType": SPACE_ID.HYGIENE,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Dedicated hygiene room for handwashing, sanitation, or clinical cleaning. "
            "Typically includes sinks, disinfectant dispensers, and hygiene storage."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_hygiene",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 2,
                "widthInches": 72,   # 6'-0"
                "lengthInches": 96,  # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "standard_hygiene",
                "treatmentRoomsMin": 2,
                "treatmentRoomsMax": None,
                "widthInches": 96,   # 8'-0"
                "lengthInches": 120,  # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 2,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": 60,  # ~5' from corridor
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
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
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.CONNECTOR,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.6,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Private Room

PRIVATE_RULES = {

    "identity": {
        "roomType": SPACE_ID.PRIVATE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Private consultation or patient room for one-on-one interaction, "
            "treatment, or examination. Provides privacy, sound separation, and personal space."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_private",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 1,
                "widthInches": 96,   # 8'-0"
                "lengthInches": 120, # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_private",
                "treatmentRoomsMin": 2,
                "treatmentRoomsMax": None,
                "widthInches": 120,  # 10'-0"
                "lengthInches": 144, # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 2,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "distanceMaxInches": 60,  # ~5' from corridor
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
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
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 0.9,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,  # Ensure privacy
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Surgical Room

SURGICAL_RULES = {

    "identity": {
        "roomType": SPACE_ID.SURGICAL,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Surgical or procedure room designed for sterile procedures. "
            "Requires strict separation from public areas, controlled access, "
            "and adjacency to support spaces (prep, scrub, recovery)."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_surgical",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": None,
                "widthInches": 144,  # 12'-0"
                "lengthInches": 180, # 15'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 24,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 1,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": 60,  # ~5' from corridor
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 44,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,  # prep, scrub, recovery
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.STERILIZATION,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 1.0,
            },
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 72,   # ~6'
                "optimizationWeight": 0.8,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.FRONT_OF_HOUSE,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.8,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 1.0,
        },
    },
}

# Open Bay Room

OPEN_BAY_RULES = {

    "identity": {
        "roomType": SPACE_ID.OPEN_BAY,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Open bay clinical area with multiple patient stations. "
            "Requires visibility for monitoring, adjacency to nursing stations, "
            "and controlled access from clinical corridors."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_open_bay",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": None,
                "widthInches": 240,  # 20'-0"
                "lengthInches": 360, # 30'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 24,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.NEAREST_MATCH,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },
    
    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 2,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": 60,  # ~5' max from corridor
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 44,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.NURSING,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 120,  # ~10'
                "optimizationWeight": 1.0,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.NURSING,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
            SPACE_ID.NURSING,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 1.0,
        },
    },
}

# Brushing Station

BRUSHING_STATION_RULES = {

    "identity": {
        "roomType": SPACE_ID.BRUSHING_STATION,
        "category": ROOM_CATEGORY.PUBLIC,
        "description": (
            "Shared brushing and handwashing station for patients, typically "
            "used before or after treatment. Often semi-open, highly visible, "
            "and located near waiting or hygiene areas."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # One brushing station cluster per clinic is typical
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.NONE,
            },
            {
                # Scale with patient volume / occupancy
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_THRESHOLD,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "compact_brushing_station",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 96,   # 8'-0"
                "lengthInches": 72,  # 6'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "expanded_brushing_station",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 144,  # 12'-0"
                "lengthInches": 96,  # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 24,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                # Should be accessible from public circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Often directly adjacent to waiting or hygiene areas
                "target": SPACE_ID.PATIENT_LOUNGE,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.6,
            },
            {
                "target": SPACE_ID.CHECK_OUT,
                "maxDistanceInches": 180,  # ~15'
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                # Avoid sterile or surgical spaces
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Avoid visibility from private or staff-only spaces
                "target": SPACE_GROUP.PRIVATE,
                "hard": False,
            },
        ],
        "mustBeVisibleFrom": [
            {
                # Staff or parents should have passive visibility
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
        "mustNotTerminateInto": [
            SPACE_GROUP.CLINICAL,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Recovery Room

RECOVERY_RULES = {

    "identity": {
        "roomType": SPACE_ID.RECOVERY,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Post-procedure recovery space for patients emerging from "
            "sedation or surgery. Supports monitoring, privacy, and staff "
            "observation prior to discharge."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Recovery required when surgical or sedation procedures exist
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.IF_PRESENT,
            },
            {
                # Optional additional recovery bays based on volume
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": None,
                "max": None,
                "condition": CONDITION_ENUM.IF_GREATER_THAN,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_patient_recovery",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 4,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 120,  # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "multi_bay_recovery",
                "treatmentRoomsMin": 5,
                "treatmentRoomsMax": None,
                "widthInches": 144,   # 12'-0"
                "lengthInches": 240,  # 20'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 36,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,  # Staff + optional secondary egress
            }
        ],
        "entryConstraints": [
            {
                # Must be easily reachable from surgical / sedation areas
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": 300,  # ~25'
                "hard": True,
            },
            {
                # Avoid direct public access
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID.SURGICAL,
                "condition": CONDITION_ENUM.IF_PRESENT,
                "hard": True,
            },
            {
                "target": SPACE_ID.CLINICAL_CORRIDOR,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                # Nursing / staff monitoring nearby
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.8,
            },
            {
                # Restroom access after recovery
                "target": SPACE_GROUP.PRIVATE,
                "maxDistanceInches": 240,
                "optimizationWeight": 0.6,
            },
        ],
        "separation": [
            {
                # Must not open directly to waiting / check-in
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Patient privacy is critical
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            {
                # Staff must be able to observe patients
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,  # May be via glazing, monitors, or doors
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            # Favor proximity to surgical core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Records Room

RECORDS_RULES = {

    "identity": {
        "roomType": SPACE_ID.RECORDS,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Secure storage space for patient records, charts, and "
            "administrative documentation. Intended for staff-only access "
            "with heightened privacy and data protection requirements."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Typically required when physical records are maintained
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_PRESENT,
            },
            {
                # Optional if fully digital practice
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.IF_ABSENT,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "compact_records_storage",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 96,   # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "expanded_records_storage",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 144,  # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 24,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,  # Single controlled access point
            }
        ],
        "entryConstraints": [
            {
                # Must not be publicly accessible
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Prefer access from staff/admin circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.ADMIN,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # ADA applies only if staff regularly occupy space
            "minClearWidthInches": 32,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Commonly near admin or staff work areas
                "target": SPACE_GROUP.ADMIN,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.BUSINESS_OFFICE,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.8,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.4,
            },
        ],
        "separation": [
            {
                # Hard privacy separation
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Records must never be visible to patients or visitors
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.ADMIN,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            # Favor administrative cluster rather than clinical core
            "reference": SPACE_GROUP.ADMIN,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.9,
        },
    },
}

# Changing Room

CHANGING_RULES = {

    "identity": {
        "roomType": SPACE_ID.CHANGING,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Private changing room for patients or staff to change clothing, "
            "store personal items, or prepare for clinical procedures."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Typically required for procedures involving gowns or uniforms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 2,
                "condition": CONDITION_ENUM.IF_PRESENT,
            },
            {
                # Optional in practices without changing needs
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 0,
                "max": 1,
                "condition": CONDITION_ENUM.IF_ABSENT,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_person_changing",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": 6,
                "widthInches": 60,     # 5'-0"
                "lengthInches": 72,    # 6'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "accessible_or_staff_changing",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 72,     # 6'-0"
                "lengthInches": 96,    # 8'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                # Must not open directly to public waiting
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Typically accessed from clinical or staff circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": False,
            },
        ],
        "ada": {
            # TODO: Confirm whether this changing room must be fully ADA accessible
            "minClearWidthInches": 32,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Often near treatment or recovery spaces
                "target": SPACE_GROUP.CLINICAL,
                "condition": CONDITION_ENUM.NONE,
                "hard": False,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.RECOVERY,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.6,
            },
            {
                "target": SPACE_ID.TREATMENT_ROOM,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.4,
            },
        ],
        "separation": [
            {
                # Privacy requirement
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.CLINICAL,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            # Bias toward clinical zone but not the core
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.5,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Nursing Room

NURSING_RULES = {

    "identity": {
        "roomType": SPACE_ID.NURSING,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Clinical nursing support space used for charting, care coordination, "
            "clinical prep, and staff observation of treatment areas. "
            "Not intended for primary patient treatment."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # One nursing station typically supports multiple treatment rooms
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_PRESENT,
            },
            {
                # Larger clinics may require multiple stations
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 2,
                "max": None,
                "condition": CONDITION_ENUM.IF_GREATER_THAN,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "small_nursing_station",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 6,
                "widthInches": 96,     # 8'-0"
                "lengthInches": 120,   # 10'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_nursing_station",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 120,    # 10'-0"
                "lengthInches": 144,   # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Typically one primary entry
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                # Must not open directly to public waiting
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should be accessed from clinical circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            # TODO: Confirm whether nursing station requires full ADA compliance
            "minClearWidthInches": 32,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Strong adjacency to treatment rooms
                "target": SPACE_GROUP.CLINICAL,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.STORAGE_CLOSET,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.7,
            },
            {
                "target": SPACE_ID.RECOVERY,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.5,
            },
            {
                "target": SPACE_ID.MED_GAS,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.6,
            },
        ],
        "separation": [
            {
                # Avoid public exposure
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
            {
                # Avoid administrative noise overlap
                "target": SPACE_GROUP.ADMIN,
                "hard": False,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # PHI protection
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            {
                # Nurses should visually monitor treatment areas
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            },
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.CLINICAL,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            # Nursing functions best when centrally located in clinical zone
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 1.0,
        },
    },
}

# Laundry Room

LAUNDRY_RULES = {

    "identity": {
        "roomType": SPACE_ID.LAUNDRY,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Clinical support space for laundering, staging, and handling of "
            "soiled and clean linens, towels, and staff garments. "
            "Not patient-facing."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                # Small clinics typically require at least one laundry room
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 1,
                "max": 1,
                "condition": CONDITION_ENUM.IF_PRESENT,
            },
            {
                # Larger clinics or high-volume operations may require more
                "driver": COUNT_DRIVER_ENUM.TREATMENT_ROOMS,
                "min": 2,
                "max": None,
                "condition": CONDITION_ENUM.IF_GREATER_THAN,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "compact_laundry",
                "treatmentRoomsMin": 1,
                "treatmentRoomsMax": 6,
                "widthInches": 72,     # 6'-0"
                "lengthInches": 96,    # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "full_laundry",
                "treatmentRoomsMin": 7,
                "treatmentRoomsMax": None,
                "widthInches": 96,     # 8'-0"
                "lengthInches": 144,   # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
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
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": False,
        },
    },

    "access": {
        "entryCountRules": [
            {
                # Typically one controlled staff entry
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 1,
            }
        ],
        "entryConstraints": [
            {
                # Must not open directly to public areas
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                # Should be accessed from clinical/service circulation
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CLINICAL,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            # TODO: Confirm ADA requirements if staff-only room is exempt
            "minClearWidthInches": 32,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                # Direct access to service circulation is important
                "target": SPACE_GROUP.CLINICAL,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            },
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.STORAGE_CLOSET,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.7,
            },
            {
                "target": SPACE_ID.HYGIENE,
                "maxDistanceInches": 180,
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                # Infection control and noise concerns
                "target": SPACE_GROUP.CLINICAL,
                "hard": False,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                # Soiled materials must not be visible publicly
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_GROUP.CLINICAL,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            # Laundry should bias toward service zones, not public center
            "reference": SPACE_GROUP.PUBLIC,
            "weight": 0.6,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Server Room

SERVER_CLOSET_RULES = {

    "identity": {
        "roomType": SPACE_ID.SERVER_CLOSET,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Dedicated server and IT equipment closet housing network racks, "
            "telecom equipment, and associated electrical infrastructure. "
            "Requires restricted access, cooling, and proximity to staff areas."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            },
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_server_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 96,   # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_server_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 144,  # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    #orientation not rlly needed?

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
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 32,  # Typical closet / service access
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 240,  # ~20'
                "optimizationWeight": 0.7,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.SUPPORT,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Janitor Closet

JANITOR_CLOSET_RULES = {

    "identity": {
        "roomType": SPACE_ID.JANITOR_CLOSET,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Janitor or environmental services closet used for storage of "
            "cleaning supplies, mop sink, and housekeeping equipment. "
            "Requires service access and separation from public-facing areas."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.DERIVED,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.BUILDING_SQFT,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "minimum_janitor_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 60,   # 5'-0"
                "lengthInches": 60,  # 5'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "large_janitor_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 72,   # 6'-0"
                "lengthInches": 96,  # 8'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.END,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 32,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 300,  # ~25'
                "optimizationWeight": 0.6,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.SUPPORT,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.9,
        },
    },
}

# Medical Gas Room

MED_GAS_RULES = {

    "identity": {
        "roomType": SPACE_ID.MED_GAS,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Dedicated medical gas storage or manifold room for oxygen, nitrous oxide, "
            "or other medical gases. Typically restricted access, non-public, "
            "and separated from patient-facing spaces."
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
                # TODO: Confirm treatment room threshold at which med gas is required
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "minimum_med_gas_room",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 96,   # 8'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "expanded_med_gas_room",
                "treatmentRoomsMin": 8,
                "treatmentRoomsMax": None,
                "widthInches": 96,    # 8'-0"
                "lengthInches": 120,  # 10'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.END,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PATIENT_FACING,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 32,
            "requiredEntries": 1,
            # TODO: Confirm if ADA access is required by jurisdiction or staff-only exemption
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": None,
                "optimizationWeight": 0.7,
            },
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 360,  # ~30'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.4,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 1.0,
        },
    },
}

# Storage Closet

STORAGE_CLOSET_RULES = {

    "identity": {
        "roomType": SPACE_ID.STORAGE_CLOSET,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Small storage closet for supplies, equipment, or general storage. "
            "Typically staff-only access, not patient-facing."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_storage_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 48,    # 4'-0"
                "lengthInches": 60,   # 5'-0"
                "areaSqIn": None,
                "longAxisVariable": False,
                "longAxisIncrementPerDoorInches": None,
            },
            {
                "label": "medium_storage_closet",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 60,    # 5'-0"
                "lengthInches": 72,   # 6'-0"
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
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BETWEEN,
            "connectsCorridors": False,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.END,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 32,
            "requiredEntries": 1,
            # TODO: Confirm if ADA compliance is required for staff-only storage
        },
    },

    "adjacency": {
        "direct": [],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.STAFF,
                "maxDistanceInches": 300,  # 25'
                "optimizationWeight": 0.8,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 360,  # 30'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PATIENT_FACING,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.STAFF,
            "weight": 0.3,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Shipping Recieving Room

SHIP_REC_RULES = {

    "identity": {
        "roomType": SPACE_ID.SHIP_REC,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Shipping and receiving area for incoming and outgoing supplies, "
            "equipment, and materials. Staff-only access. May require loading dock access."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_ship_rec",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 180,  # 15'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
            {
                "label": "medium_ship_rec",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 180,   # 15'-0"
                "lengthInches": 240,  # 20'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.END,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.END,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.STAFF,
                "distanceMaxInches": None,
                "hard": True,
            },
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_NOT_FROM,
                "target": SPACE_GROUP.PUBLIC,
                "distanceMaxInches": None,
                "hard": True,
            },
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
            # TODO: Confirm if ADA is needed for shipping/receiving access
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.STAFF,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.SUPPORT,
                "maxDistanceInches": 120,  # 10'
                "optimizationWeight": 0.9,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "maxDistanceInches": 360,  # 30'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.STAFF,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
            # TODO: Consider connecting to MECHANICAL or LOADING areas if layout allows
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
            SPACE_ID.CHECK_OUT,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.STAFF,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Conference Room

CONFERENCE_RULES = {

    "identity": {
        "roomType": SPACE_ID.CONFERENCE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Conference room for staff meetings, presentations, and collaboration. "
            "Staff-access only, may have AV equipment and seating for 6–12 people."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "small_conference",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 180,  # 15'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
            {
                "label": "medium_conference",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 180,   # 15'-0"
                "lengthInches": 240,  # 20'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 1,
                "maxEntries": 2,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.STAFF,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.STAFF,
                "maxDistanceInches": 240,  # 20'
                "optimizationWeight": 0.8,
            },
            {
                "target": SPACE_GROUP.PUBLIC,
                "maxDistanceInches": 360,  # 30'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.STAFF,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CROSSOVER_HALLWAY,
            # TODO: Confirm if must connect to STAFF_LOUNGE or ADMIN zones
        ],
        "mustNotTerminateInto": [
            SPACE_ID.PATIENT_LOUNGE,
            SPACE_ID.CHECK_IN,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PRIVATE,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.8,
        },
    },
}

# Associate Office

ASSOCIATE_OFFICE_RULES = {

    "identity": {
        "roomType": SPACE_ID.ASSOCIATE_OFFICE,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Private office for associate staff. Includes workspace, desk, "
            "and potentially small meeting area for 1-2 people."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": None,  # TODO: Confirm max number per floor
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_associate_office",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 120,   # 10'-0"
                "lengthInches": 144,  # 12'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PRIVATE,
                "distanceMaxInches": None,
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_GROUP.ADMIN,
                "maxDistanceInches": 240,  # 20'
                "optimizationWeight": 0.7,
            },
            {
                "target": SPACE_GROUP.STAFF,
                "maxDistanceInches": 300,  # 25'
                "optimizationWeight": 0.5,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.STAFF,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CROSSOVER_HALLWAY,  # TODO: confirm connection preference
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CHECK_IN,
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PRIVATE,
            "weight": 0.6,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

# Associates Restroom

ASSOCIATE_RESTROOM_RULES = {

    "identity": {
        "roomType": SPACE_ID.ASSOCIATE_RESTROOM,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Restroom designated for associate/staff use. Typically includes "
            "toilet(s), sink(s), and may be single or multi-stall depending on staff size."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.OCCUPANCY,
                "min": 1,
                "max": None,  # TODO: Confirm if more than 1 restroom is needed for larger floors
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "single_staff_restroom",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 72,    # 6'-0"
                "lengthInches": 84,   # 7'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            },
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.BACK,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PRIVATE,
                "distanceMaxInches": 120,  # within 10' of offices
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.ASSOCIATE_OFFICE,
                "maxDistanceInches": 120,  # 10' max from offices
                "optimizationWeight": 0.8,
            },
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            },
            {
                "target": SPACE_GROUP.CLINICAL,
                "hard": True,
            },
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CROSSOVER_HALLWAY,  # TODO: confirm exact corridor connection
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CHECK_IN,
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PRIVATE,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Marketing Room

MARKETING_RULES = {

    "identity": {
        "roomType": SPACE_ID.MARKETING,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Office space for marketing staff. Typically includes desks, workstations, "
            "and collaborative areas for marketing/admin activities."
        ),
    },

    "existence": {
        "trigger": TRIGGER_ENUM.ALWAYS,
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM.FIXED,
                "min": 1,
                "max": 1,  # TODO: Confirm if more than 1 marketing office is needed per floor
                "condition": CONDITION_ENUM.NONE,
            }
        ],
    },

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_marketing_office",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 144,   # 12'-0"
                "lengthInches": 180,  # 15'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PRIVATE,
                "distanceMaxInches": 120,  # within 10' of admin cluster
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.TEAM_LEADER,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.8,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CROSSOVER_HALLWAY,  # TODO: Confirm exact corridor or adjacency
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CHECK_IN,
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PRIVATE,
            "weight": 0.7,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# Team Leader Room

TEAM_LEADER_RULES = {

    "identity": {
        "roomType": SPACE_ID.TEAM_LEADER,
        "category": ROOM_CATEGORY.PRIVATE,
        "description": (
            "Private office for the team leader or office manager. "
            "Typically includes desk, seating for visitors, and administrative workspace."
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

    "geometry": {
        "shape": SHAPE_ENUM.RECTANGULAR,
        "dimensionModels": [
            {
                "label": "standard_team_leader_office",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 144,   # 12'-0"
                "lengthInches": 192,  # 16'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 12,
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
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
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.PRIVATE,
                "distanceMaxInches": 120,  # within 10' of admin cluster
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 1,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.MARKETING,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.8,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": True,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.MARKETING,
                "hard": False,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CROSSOVER_HALLWAY,  # TODO: Confirm exact corridor
        ],
        "mustNotTerminateInto": [
            SPACE_ID.CHECK_IN,
            SPACE_ID.PATIENT_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.PRIVATE,
            "weight": 0.8,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.6,
        },
    },
}

# patient Care Center

PATIENT_CARE_CENTER_RULES = {

    "identity": {
        "roomType": SPACE_ID.PATIENT_CARE_CENTER,
        "category": ROOM_CATEGORY.CLINICAL,
        "description": (
            "Central clinical area for patient services, coordination, "
            "and support. May include patient intake, coordination desks, "
            "and waiting or observation zones."
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

    "geometry": {
        "shape": SHAPE_ENUM.RECTILINEAR,
        "dimensionModels": [
            {
                "label": "standard_patient_care_center",
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "widthInches": 300,   # 25'-0"
                "lengthInches": 480,  # 40'-0"
                "areaSqIn": None,
                "longAxisVariable": True,
                "longAxisIncrementPerDoorInches": 24,
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM.MINIMUM,
    },

    "orientation": {
        LAYOUT_ENUM.NARROW: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.PARALLEL,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.H_LAYOUT: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
        LAYOUT_ENUM.THREE_LAYER_CAKE: {
            "allowed": True,
            "longAxisRelation": AXIS_RELATION_ENUM.NONE,
            "placementHint": PLACEMENT_ENUM.CENTER,
            "connectsCorridors": True,
        },
    },

    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": None,
                "treatmentRoomsMax": None,
                "minEntries": 2,
                "maxEntries": 3,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM.ENTRY_FROM,
                "target": SPACE_GROUP.CORRIDORS,
                "distanceMaxInches": 60,  # 5' from main corridor
                "hard": True,
            }
        ],
        "ada": {
            "minClearWidthInches": 36,
            "requiredEntries": 2,
        },
    },

    "adjacency": {
        "direct": [
            {
                "target": SPACE_GROUP.CLINICAL,
                "condition": CONDITION_ENUM.NONE,
                "hard": True,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID.TREATMENT_COORDINATION,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.9,
            },
            {
                "target": SPACE_ID.CHECK_IN,
                "maxDistanceInches": 120,
                "optimizationWeight": 0.8,
            }
        ],
        "separation": [
            {
                "target": SPACE_GROUP.PUBLIC,
                "hard": False,
            }
        ],
    },

    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_GROUP.PRIVATE,
                "hard": False,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID.CHECK_IN,
                "hard": True,
            }
        ],
    },

    "circulation": {
        "role": CIRCULATION_ROLE_ENUM.DESTINATION,
        "mustConnect": [
            SPACE_ID.CLINICAL_CORRIDOR,
            SPACE_ID.CROSSOVER_HALLWAY,
        ],
        "mustNotTerminateInto": [
            SPACE_ID.STAFF_LOUNGE,
        ],
    },

    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP.CLINICAL,
            "weight": 0.9,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": 0.7,
        },
    },
}

ROOM_RULES = {
    SPACE_ID.STERILIZATION: STERILIZATION_RULES,
    SPACE_ID.LAB: LAB_RULES,
    SPACE_ID.CONSULT: CONSULT_RULES,
    SPACE_ID.PATIENT_RESTROOM: PATIENT_RESTROOM_RULES,
    SPACE_ID.TREATMENT_COORDINATION: TREATMENT_COORDINATION_RULES,
    SPACE_ID.MOBILE_TECH: MOBILE_TECH_RULES,
    SPACE_ID.DOCTORS_ON_DECK: DOCTORS_ON_DECK_RULES,
    SPACE_ID.DOCTOR_OFFICE: DOCTOR_OFFICE_RULES,
    SPACE_ID.DOCTOR_PRIVATE_RESTROOM: DOCTOR_PRIVATE_RESTROOM_RULES,
    SPACE_ID.OFFICE_MANAGER: OFFICE_MANAGER_RULES,
    SPACE_ID.BUSINESS_OFFICE: BUSINESS_OFFICE_RULES,
    SPACE_ID.ALT_BUSINESS_OFFICE: ALT_BUSINESS_OFFICE_RULES,
    SPACE_ID.STAFF_LOUNGE: STAFF_LOUNGE_RULES,
    SPACE_ID.PATIENT_LOUNGE: PATIENT_LOUNGE_RULES,
    SPACE_ID.CROSSOVER_HALLWAY: CROSSOVER_HALLWAY_RULES,
    SPACE_ID.CLINICAL_CORRIDOR: CLINICAL_CORRIDOR_RULES,
    SPACE_ID.TREATMENT_ROOM: TREATMENT_ROOM_RULES,
    SPACE_ID.CHECK_IN: CHECK_IN_RULES,
    SPACE_ID.CHECK_OUT: CHECK_OUT_RULES,
    SPACE_ID.MECHANICAL: MECHANICAL_RULES,
    SPACE_ID.STAFF_RESTROOM: STAFF_RESTROOM_RULES,
    SPACE_ID.DOCTOR_NOOK: DOCTOR_NOOK_RULES,
    SPACE_ID.VESTIBULE: VESTIBULE_RULES,
    SPACE_ID.CHILDRENS: CHILDRENS_RULES,
    SPACE_ID.REFRESHMENT: REFRESHMENT_RULES,
    SPACE_ID.RETAIL: RETAIL_RULES,
    SPACE_ID.IMAGING: IMAGING_RULES,
    SPACE_ID.PHOTO: PHOTO_RULES,
    SPACE_ID.MULTI_STALLS: MULTI_STALLS_RULES,
    SPACE_ID.TOY: TOY_RULES,
    SPACE_ID.UNIVERSAL: UNIVERSAL_RULES,
    SPACE_ID.HYGIENE: HYGIENE_RULES,
    SPACE_ID.PRIVATE: PRIVATE_RULES,
    SPACE_ID.SURGICAL: SURGICAL_RULES,
    SPACE_ID.OPEN_BAY: OPEN_BAY_RULES,
    SPACE_ID.BRUSHING_STATION: BRUSHING_STATION_RULES,
    SPACE_ID.RECOVERY: RECOVERY_RULES,
    SPACE_ID.RECORDS: RECORDS_RULES,
    SPACE_ID.CHANGING: CHANGING_RULES,
    SPACE_ID.NURSING: NURSING_RULES,
    SPACE_ID.LAUNDRY: LAUNDRY_RULES,
    SPACE_ID.SERVER_CLOSET: SERVER_CLOSET_RULES,
    SPACE_ID.JANITOR_CLOSET: JANITOR_CLOSET_RULES,
    SPACE_ID.MED_GAS: MED_GAS_RULES,
    SPACE_ID.STORAGE_CLOSET: STORAGE_CLOSET_RULES,
    SPACE_ID.SHIP_REC: SHIP_REC_RULES,
    SPACE_ID.CONFERENCE: CONFERENCE_RULES,
    SPACE_ID.ASSOCIATE_OFFICE: ASSOCIATE_OFFICE_RULES,
    SPACE_ID.ASSOCIATE_RESTROOM: ASSOCIATE_RESTROOM_RULES,
    SPACE_ID.MARKETING: MARKETING_RULES,
    SPACE_ID.TEAM_LEADER: TEAM_LEADER_RULES,
    SPACE_ID.PATIENT_CARE_CENTER: PATIENT_CARE_CENTER_RULES,
}