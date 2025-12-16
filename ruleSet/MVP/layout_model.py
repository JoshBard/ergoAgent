# layout_model.py
#
# Skeleton MIP layout model on a 1-inch discrete grid.
# - Rooms are axis-aligned rectangles with integer coordinates (x, y, w, h)
# - Entrances are discrete integer positions on the rectangle perimeter
# - Constraint details live in layout_constraints.py

from ortools.linear_solver import pywraplp # pyright: ignore[reportMissingImports]

from ruleset_simplified import ROOM_RULES
from ruleset_consts import (
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
)

from layout_constraints import (
    add_room_bounds_constraints,
    add_non_overlap_constraints,
    add_entry_bounds_constraints,
    add_simple_entry_from_corridor_constraints,
    add_adjacency_constraints_from_rules,
    add_visibility_constraints_from_rules,
    add_room_min_constraints_from_rules,
    add_room_max_constraints_from_rules,
    add_room_ideal_size_soft_objective,
)

TREATMENT_ROOM_TYPES = {DUAL_ENTRY_TREATMENT, SIDE_TOE_TREATMENT, TOE_TREATMENT}


def _make_instance_id(room_type: str, idx: int) -> str:
    return f"{room_type}__{idx}"


def build_layout_model(
    building_width_in,
    building_height_in,
    rooms,
    num_treatment_rooms,
    max_entrances_per_room=2,
):
    """
    Build a mixed-integer model on a 1-inch discrete grid.

    - building_width_in, building_height_in: total shell size in inches
    - rooms: list of room INSTANCE identifiers (e.g., "TOE_TREATMENT__0")
    - num_treatment_rooms: scalar used by tiered rules (sterilization)
    - max_entrances_per_room: maximum number of door locations we allow per room in v1

    Returns:
        solver, vars_dict
    """
    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("Could not create CBC solver")

    # -------------------------------
    # Variables
    # -------------------------------
    x = {}
    y = {}
    w = {}
    h = {}

    for r in rooms:
        x[r] = solver.IntVar(0, building_width_in, f"x_{r}")
        y[r] = solver.IntVar(0, building_height_in, f"y_{r}")
        w[r] = solver.IntVar(1, building_width_in, f"w_{r}")
        h[r] = solver.IntVar(1, building_height_in, f"h_{r}")

    entrance_x = {}
    entrance_y = {}
    entrance_active = {}

    for r in rooms:
        for k in range(max_entrances_per_room):
            entrance_x[(r, k)] = solver.IntVar(0, building_width_in, f"door_x_{r}_{k}")
            entrance_y[(r, k)] = solver.IntVar(0, building_height_in, f"door_y_{r}_{k}")
            entrance_active[(r, k)] = solver.BoolVar(f"door_active_{r}_{k}")

    # -------------------------------
    # Rules lookup per instance
    # -------------------------------
    # Your constraints functions do ROOM_RULES.get(r, {}) where r is the room id.
    # For multiple instances, make a rules dict keyed by instance id.
    ROOM_RULES_BY_INSTANCE = {}
    for r in rooms:
        base_type = r.split("__", 1)[0]
        ROOM_RULES_BY_INSTANCE[r] = ROOM_RULES.get(base_type, {})

    # -------------------------------
    # Constraints
    # -------------------------------
    add_room_bounds_constraints(
        solver, rooms, x, y, w, h, building_width_in, building_height_in
    )

    add_entry_bounds_constraints(
        solver, rooms, x, y, w, h, entrance_x, entrance_y, entrance_active
    )

    add_non_overlap_constraints(solver, rooms, x, y, w, h)

    # Corridor-specific constraints:
    # If you include multiple corridors later, you’ll want to pick a specific corridor instance.
    corridor_instances = [r for r in rooms if r.split("__", 1)[0] == CLINICAL_CORRIDOR]
    if corridor_instances:
        corridor_room_id = corridor_instances[0]
        add_simple_entry_from_corridor_constraints(
            solver,
            rooms,
            x,
            y,
            w,
            h,
            entrance_x,
            entrance_y,
            entrance_active,
            corridor_room_id=corridor_room_id,
        )

    add_adjacency_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES_BY_INSTANCE)
    add_visibility_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES_BY_INSTANCE)

    add_room_min_constraints_from_rules(
        solver, rooms, w, h, num_treatment_rooms, ROOM_RULES_BY_INSTANCE
    )
    add_room_max_constraints_from_rules(
        solver, rooms, w, h, num_treatment_rooms, ROOM_RULES_BY_INSTANCE
    )

    ideal_obj, _ = add_room_ideal_size_soft_objective(
        solver, rooms, w, h, ROOM_RULES_BY_INSTANCE, weight=1.0
    )

    # -------------------------------
    # Objective
    # -------------------------------
    total_size = solver.Sum([w[r] + h[r] for r in rooms])
    solver.Minimize(total_size + ideal_obj)

    vars_dict = {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "entrance_x": entrance_x,
        "entrance_y": entrance_y,
        "entrance_active": entrance_active,
        "ROOM_RULES_BY_INSTANCE": ROOM_RULES_BY_INSTANCE,
    }

    return solver, vars_dict


def _prompt_nonnegative_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a non-negative integer (0 or more).")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def main():
    print("=== Floorplan MIP Layout ===")
    print("Enter building shell size (inches).")

    building_width_in = _prompt_nonnegative_int("Building width in inches: ")
    building_height_in = _prompt_nonnegative_int("Building height in inches: ")

    if building_width_in <= 0 or building_height_in <= 0:
        print("Building dimensions must be positive.")
        return

    room_types = [
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
    ]

    print("\nEnter desired count for each room type (0 for none).\n")

    selected_rooms = []
    counts_by_type = {}
    for rt in room_types:
        count = _prompt_nonnegative_int(f"{rt}: ")
        counts_by_type[rt] = count

        if count > 0 and rt not in ROOM_RULES:
            print(f"  [warning] No ROOM_RULES entry for '{rt}', it will have only generic constraints.")

        for i in range(count):
            selected_rooms.append(_make_instance_id(rt, i))

    if not selected_rooms:
        print("No rooms selected (all counts were 0). Nothing to solve.")
        return

    # Sum treatment room kinds
    num_treatment_rooms = sum(counts_by_type.get(t, 0) for t in TREATMENT_ROOM_TYPES)

    solver, vars_dict = build_layout_model(
        building_width_in=building_width_in,
        building_height_in=building_height_in,
        rooms=selected_rooms,
        num_treatment_rooms=num_treatment_rooms,
    )

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print("\nFound layout (all dimensions in inches):")
        for r in selected_rooms:
            x_var = vars_dict["x"][r]
            y_var = vars_dict["y"][r]
            w_var = vars_dict["w"][r]
            h_var = vars_dict["h"][r]
            base = r.split("__", 1)[0]
            print(
                f"{r} [{base}]: (x={x_var.solution_value():.0f}, "
                f"y={y_var.solution_value():.0f}, "
                f"w={w_var.solution_value():.0f}, "
                f"h={h_var.solution_value():.0f})"
            )
        print(f"\nnum_treatment_rooms = {num_treatment_rooms}")
    else:
        print("No optimal solution found; status:", status)


if __name__ == "__main__":
    main()
