from core import *

RoomSchema = {

    
    # Identity & Classification
    
    "identity": {
        "roomType": SPACE_ID,                 # enum
        "category": ROOM_CATEGORY,           # CLINICAL | PUBLIC | PRIVATE
        "description": str | None,
    },

    
    # Existence & Counting
    
    "existence": {
        "trigger": TRIGGER_ENUM,              # always | user_input | derived
        "countRules": [
            {
                "driver": COUNT_DRIVER_ENUM,  # treatmentRooms | sqft | occupancy | fixed
                "min": int | None,
                "max": int | None,
                "condition": CONDITION_ENUM,    # or none
            }
        ]
    },

    
    # Geometry Envelope (Room Outline Only)
    
    "geometry": {
        "shape": SHAPE_ENUM,                  # rectangular | rectilinear | irregular
        "dimensionModels": [
            {
                "label": str,
                "treatmentRoomsMin": int | None,
                "treatmentRoomsMax": int | None,
                "widthInches": int | None,
                "lengthInches": int | None,
                "areaSqIn": int | None,
                "longAxisVariable": bool,
                "longAxisIncrementPerDoorInches": int | None,
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM
    },

    
    # Layout-Specific Orientation Rules
    
    "orientation": {
        LAYOUT_ENUM: {
            "allowed": bool,
            "longAxisRelation": AXIS_RELATION_ENUM | None,
            "placementHint": PLACEMENT_ENUM | None,
            "connectsCorridors": bool | None,
        }
    },

    
    # Access & Entries
    
    "access": {
        "entryCountRules": [
            {
                "treatmentRoomsMin": int | None,
                "treatmentRoomsMax": int | None,
                "minEntries": int,
                "maxEntries": int | None,
            }
        ],
        "entryConstraints": [
            {
                "kind": ENTRY_RULE_ENUM,
                "target": SPACE_ID | SPACE_GROUP | None,
                "distanceMaxInches": int | None,
                "hard": bool,
            }
        ],
        "ada": {
            "minClearWidthInches": int,
            "requiredEntries": int,
        }
    },

    
    # Adjacency & Proximity
    
    "adjacency": {
        "direct": [
            {
                "target": SPACE_ID | SPACE_GROUP,
                "condition": CONDITION_ENUM | None,
                "hard": bool,
            }
        ],
        "preferredProximity": [
            {
                "target": SPACE_ID | SPACE_GROUP,
                "maxDistanceInches": int | None,
                "optimizationWeight": float,
            }
        ],
        "separation": [
            {
                "target": SPACE_ID | SPACE_GROUP,
                "hard": bool,
            }
        ]
    },

    
    # Visibility / Sightlines (Room-to-Room Only)
    
    "visibility": {
        "mustBeHiddenFrom": [
            {
                "target": SPACE_ID | SPACE_GROUP,
                "hard": bool,
            }
        ],
        "mustBeVisibleFrom": [
            {
                "target": SPACE_ID | SPACE_GROUP,
                "hard": bool,
            }
        ]
    },

    
    # Circulation Role (Graph Semantics)
    
    "circulation": {
        "role": CIRCULATION_ROLE_ENUM,         # spine | connector | destination
        "mustConnect": [SPACE_ID],
        "mustNotTerminateInto": [SPACE_ID],
    },

    
    # Optimization Hints (Soft Goals)
    
    "optimization": {
        "centerBias": {
            "reference": SPACE_GROUP | None,
            "weight": float,
        },
        "layoutCohesionBias": {
            "sameCategoryBonus": float,
        }
    }
}
