# ruleset_core.py

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
    RECEPTION,
    CHECK_IN,
    CHECK_OUT,
    MECHANICAL,
    STAFF_ENTRY,
    STAFF_RESTROOMS,
    DOCTOR_NOOK,
    PATIENT_FACING,
    PATIENT_VISUAL_ZONES,
    ADA_DOOR,
)

# -------------------------------------------------
# 1) Requirement triggers (indexable)
# -------------------------------------------------

TRIGGER_ALWAYS = 1
TRIGGER_USER_INPUT = 2
TRIGGER_TREATMENT_ROOMS_PRESENT = 3
TRIGGER_TREATMENT_ROOMS_GT_4 = 4
TRIGGER_TWO_PARALLEL_CLINICAL = 5
TRIGGER_TREATMENT_ROOMS_GE_5_NO_DOCTOR_OFFICE = 6

TRIGGER_LABELS = {
    TRIGGER_ALWAYS: "always",
    TRIGGER_USER_INPUT: "userInput",
    TRIGGER_TREATMENT_ROOMS_PRESENT: "treatmentRoomsPresent",
    TRIGGER_TREATMENT_ROOMS_GT_4: "treatmentRooms>4",
    TRIGGER_TWO_PARALLEL_CLINICAL: "twoParallelClinicalCorridors",
    TRIGGER_TREATMENT_ROOMS_GE_5_NO_DOCTOR_OFFICE: (
        "treatmentRooms>=5WithoutOtherDoctorOfficeOnClinicalFloor"
    ),
}

# -------------------------------------------------
# 2) Rule kinds (indexable)
# -------------------------------------------------

RULE_ENTRY_FROM = 1
RULE_ENTRY_NOT_FROM = 2
RULE_ENTRY_WITHIN_DISTANCE = 3
RULE_NEAR_SPACE = 4
RULE_ADJACENT = 5
RULE_SEPARATE = 6
RULE_AVOID_VISIBILITY = 7
RULE_REQUIRE_VISIBILITY = 8
RULE_NOT_WITHIN_DISTANCE = 9

RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR = 10
RULE_OPPOSITE_ENDS_ON_LONG_AXIS = 11
RULE_ENTRY_FROM_ONE_OF = 12
RULE_ENTRY_INTERNAL_CONNECTION = 13
RULE_SEPARATE_FROM_ALL_OTHER_SPACES = 14
RULE_PREFER_NEAR_CLINICAL_CENTER = 15
RULE_PREFER_NEAR_TREATMENT_CENTER = 16
RULE_NOT_TERMINATE_INTO = 17
RULE_NOT_DIRECTLY_OPPOSITE_SAME_TYPE = 18
RULE_TOE_SIDE_ENTRY_LOCATION_TBD = 19
RULE_TOE_WALL_ENTRY_FROM = 20

RULE_LABELS = {
    RULE_ENTRY_FROM: "entry_from",
    RULE_ENTRY_NOT_FROM: "entry_not_from",
    RULE_ENTRY_WITHIN_DISTANCE: "entry_within_distance",
    RULE_NEAR_SPACE: "near_space",
    RULE_ADJACENT: "adjacent",
    RULE_SEPARATE: "separate",
    RULE_AVOID_VISIBILITY: "avoid_visibility_from",
    RULE_REQUIRE_VISIBILITY: "require_visibility_from",
    RULE_NOT_WITHIN_DISTANCE: "not_within_distance",
    RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR: "not_from_any_other_room_interior",
    RULE_OPPOSITE_ENDS_ON_LONG_AXIS: "opposite_ends_on_long_axis",
    RULE_ENTRY_FROM_ONE_OF: "entry_from_one_of",
    RULE_ENTRY_INTERNAL_CONNECTION: "entry_internal_connection",
    RULE_SEPARATE_FROM_ALL_OTHER_SPACES: "separate_from_all_other_spaces",
    RULE_PREFER_NEAR_CLINICAL_CENTER: "prefer_near_clinical_center",
    RULE_PREFER_NEAR_TREATMENT_CENTER: "prefer_near_treatment_center",
    RULE_NOT_TERMINATE_INTO: "not_terminate_into",
    RULE_NOT_DIRECTLY_OPPOSITE_SAME_TYPE: "not_directly_opposite_same_type",
    RULE_TOE_SIDE_ENTRY_LOCATION_TBD: "toe_side_entry_location_TBD",
    RULE_TOE_WALL_ENTRY_FROM: "toe_wall_entry_from",
}

# -------------------------------------------------
# 3) Helper constructors – now returning KIND CODES
# -------------------------------------------------


def entry_from(space_id, hard=True):
    return {
        "kind": RULE_ENTRY_FROM,
        "space": space_id,
        "hard": hard,
    }


def entry_not_from(space_id, hard=True):
    return {
        "kind": RULE_ENTRY_NOT_FROM,
        "space": space_id,
        "hard": hard,
    }


def entry_within_distance(space_id, max_distance_inches, hard=False):
    return {
        "kind": RULE_ENTRY_WITHIN_DISTANCE,
        "space": space_id,
        "maxDistanceInches": max_distance_inches,
        "hard": hard,
    }


def near_space(space_id, max_distance_inches, hard=False):
    return {
        "kind": RULE_NEAR_SPACE,
        "space": space_id,
        "maxDistanceInches": max_distance_inches,
        "hard": hard,
    }


def direct_adjacency(space_id, hard=True):
    return {
        "kind": RULE_ADJACENT,
        "space": space_id,
        "hard": hard,
    }


def separate_from(space_id, hard=True):
    return {
        "kind": RULE_SEPARATE,
        "space": space_id,
        "hard": hard,
    }


def avoid_visibility_from(space_id_or_group, hard=False):
    return {
        "kind": RULE_AVOID_VISIBILITY,
        "source": space_id_or_group,
        "hard": hard,
    }


def require_visibility_from(space_id_or_group, hard=True):
    return {
        "kind": RULE_REQUIRE_VISIBILITY,
        "source": space_id_or_group,
        "hard": hard,
    }


def not_within_distance_of(space_id, min_distance_inches, hard=False):
    return {
        "kind": RULE_NOT_WITHIN_DISTANCE,
        "space": space_id,
        "minDistanceInches": min_distance_inches,
        "hard": hard,
    }
