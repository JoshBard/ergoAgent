from .core import *

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
                #TODO: perhaps add argument field so that condition enum doesn't hold semantics
            }
        ]
    },

    
    # Geometry Envelope (Room Outline Only)
    
    "geometry": {
        "shape": SHAPE_ENUM,                  # rectangular | rectilinear | irregular
        "derivationMode"
        "dimensionModels": [
            {
                "label": str,
                "treatmentRoomsMin": int | None,
                "treatmentRoomsMax": int | None,
                "widthInches": int | None,
                "lengthInches": int | None,
                "areaSqIn": int | None,
                "longAxisVariable": bool,   # TODO: evaluate and encode long axis when footprint being encoded
                "longAxisIncrementPerDoorInches": int | None,
                "aspectRatioRange": (float, float),
            }
        ],
        "fallbackStrategy": GEOMETRY_FALLBACK_ENUM
    },


    # Flexible capacity model to hold conditions for derived geometries
    "capacityModel": {
        "driver": CAPACITY_DRIVER_ENUM,  # seats | workstations | occupants | staff
        "derivedFrom": COUNT_DRIVER_ENUM | None,  # treatmentRooms, occupancy, etc

        "quantity": {
            "perUnit": float | None,
            "min": int | None,
            "max": int | None,
            "rounding": ROUNDING_ENUM | None,
        },

        "area": {
            "perUnitNSF": float | None,
            "baseAreaNSF": float | None,
            "buffers": [
                {
                    "label": str,
                    "minNSF": int | None,
                    "maxNSF": int | None,
                }
            ]
        }
    },

    
    # Layout-Specific Orientation Rules
    
    "orientation": {#might not be a rule so much as a success metric
        LAYOUT_ENUM: {
            "allowed": bool,
            "longAxisRelation": AXIS_RELATION_ENUM | None,  # TODO: add a relationTo field so we know what it is relative to
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
                "target": SPACE_ID | SPACE_GROUP,#TODO: maybe instead of space group do preferred dist to treatment room or other space_id
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
