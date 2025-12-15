# This holds DSL vocabulary enumerations and definitions 
# referneced by our schema'd rule set
from enum import Enum, auto

#Identity Enums:

class ROOM_CATEGORY(Enum):
    #zoning classification. Used to identify zones in BDs.
    
    CLINICAL = auto()
    PUBLIC = auto()
    PRIVATE = auto()

class SPACE_ID(Enum):
    # Room identifiers, 
    # these are only rooms we have rules for or that were mentioned in rule set.
    # rooms that arent in rule set still need labels here

    STERILIZATION = auto()
    LAB = auto()
    CONSULT = auto()
    PATIENT_RESTROOM = auto()
    TREATMENT_COORDINATION = auto()
    MOBILE_TECH = auto()
    DOCTORS_ON_DECK = auto()
    DOCTOR_OFFICE = auto()
    DOCTOR_PRIVATE_RESTROOM = auto()
    OFFICE_MANAGER = auto()
    BUSINESS_OFFICE = auto()
    ALT_BUSINESS_OFFICE = auto()
    STAFF_LOUNGE = auto()
    PATIENT_LOUNGE = auto()
    CROSSOVER_HALLWAY = auto()
    CLINICAL_CORRIDOR = auto()
    TREATMENT_ROOM = auto()
    RECEPTION = auto()
    CHECK_IN = auto()
    CHECK_OUT = auto()
    MECHANICAL = auto()
    STAFF_ENTRY = auto()
    STAFF_RESTROOMS = auto()
    DOCTOR_NOOK = auto()


#Layout and Geometry Enums:

class LAYOUT_ENUM(Enum):
    #layout modes:

    NARROW = auto()
    THREE_LAYER_CAKE = auto()
    H_LAYOUT = auto()

class SHAPE_ENUM(Enum):
    #allowed room shapes

    RECTANGULAR = auto()
    RECTILINEAR = auto()
    IRREGULAR = auto()

class GEOMETRY_FALLBACK_ENUM(Enum):
    # backup strategy options if initial generation can't be done based on inputs

    ERROR = auto()           # fail generation
    MINIMUM = auto()         # smallest valid envelope
    NEAREST_MATCH = auto()   # closest dimension model
    USER_OVERRIDE = auto()   # defer to external input


#Oritentation and Placement Enums:

class AXIS_RELATION_ENUM(Enum):
    # relationship of long axis to some refernce point (specifiable in ruleset shcema)
    
    PARALLEL = auto()
    PERPENDICULAR = auto()
    ALONG = auto()  #same as plel?
    NONE = auto()

class PLACEMENT_ENUM(Enum):
    # coarse placement indicatiors used by schema

    FRONT = auto()
    CENTER = auto()
    BACK = auto()
    BETWEEN = auto()
    END_TO_END = auto()


#Existence and Counting Enums:

class TRIGGER_ENUM(Enum):
    # when construction is triggered (does it exist in floorplan)

    ALWAYS = auto()
    USER_INPUT = auto()
    DERIVED = auto()

class COUNT_DRIVER_ENUM(Enum):
    # variable that drives count 

    TREATMENT_ROOMS = auto()
    BUILDING_SQFT = auto()
    OCCUPANCY = auto()
    FIXED = auto()

class CONDITION_ENUM(Enum):
    # modifier to add additional conditions to rules

    IF_PRESENT = auto()
    IF_ABSENT = auto()
    IF_LAYOUT = auto()
    IF_THRESHOLD = auto()
    NONE = auto()


#Access and Entry Enums:

class ENTRY_RULE_ENUM(Enum):
    #entry placement rules

    ENTRY_FROM = auto()              # must enter from target
    ENTRY_NEAR = auto()              # entry within distance
    ENTRY_NOT_FROM = auto()          # must not enter from target
    ENTRY_OPPOSITE_ENDS = auto()     # entries at opposite ends
    ENTRY_NOT_WITHIN_DISTANCE = auto()


#Adjacency and Graph Semantics:

class SPACE_GROUP(Enum):
    # course group labels for rooms,
    # can be used to avoid exploding graph from direct adjacency rules

    PATIENT_FACING = auto()
    CLINICAL = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    SUPPORT = auto()
    CORRIDORS = auto()


#Circulation graph role

class CIRCULATION_ROLE_ENUM(Enum):
    #Role of a space in the circulation graph.

    SPINE = auto()         # main corridor / backbone
    CONNECTOR = auto()     # joins spines or zones
    DESTINATION = auto()  # rooms people go to


# Visibility Semantics

class VISIBILITY_RULE_ENUM(Enum):
    # NOTE: Visibility is abstracted to adjacency + orientation.
    # No ray casting or geometry here.

    MUST_BE_HIDDEN_FROM = auto()
    MUST_BE_VISIBLE_FROM = auto()


# Optimization Semantics (Soft Objectives)

class OPTIMIZATION_REFERENCE_ENUM(Enum):    
    #Reference anchors used by optimization hints.

    CLINICAL_CENTER = auto()
    PUBLIC_CENTER = auto()
    BUILDING_CENTER = auto()
    ENTRY = auto()


# Distance & Measurement Semantics

class DISTANCE_TYPE_ENUM(Enum):
    # Defines how distances are measured.

    # NOTE:
    # This allows MIP vs graph solvers to interpret
    # distances differently without changing rules.

    EUCLIDEAN = auto()
    MANHATTAN = auto()
    GRAPH_HOPS = auto()


# NOTE:

"""
INTENTIONALLY NOT DEFINED YET:

- Detailed door geometry semantics
- Internal room zoning (clean/dirty sides)
- Line of sight obstruction logic
- Furniture or equipment constraints

These belong downstream of:
- room envelope generation
- primary constraint solving

They dont belong in this file
"""