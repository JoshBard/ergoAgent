# layout_model.py
#
# Skeleton MIP layout model on a 1-inch discrete grid.
# - Rooms are axis-aligned rectangles with integer coordinates (x, y, w, h)
# - Entrances are discrete integer positions on the rectangle perimeter
# - Constraint details live in layout_constraints.py

from ortools.linear_solver import pywraplp

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
)


def build_layout_model(building_width_in, building_height_in, rooms, max_entrances_per_room=2):
    """
    Build a mixed-integer model on a 1-inch discrete grid.

    - building_width_in, building_height_in: total shell size in inches
    - rooms: list of room type identifiers to include (strings from ruleset_consts)
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
    # Rectangles: (x, y) bottom-left, (w, h) width & height, all in inches
    x = {}
    y = {}
    w = {}
    h = {}

    for r in rooms:
        # For now, domain 0..building dimension; you can narrow later from ROOM_RULES[r]["dimensions"]
        x[r] = solver.IntVar(0, building_width_in, f"x_{r}")
        y[r] = solver.IntVar(0, building_height_in, f"y_{r}")
        w[r] = solver.IntVar(1, building_width_in, f"w_{r}")
        h[r] = solver.IntVar(1, building_height_in, f"h_{r}")

    # Entrances:
    # entrance_x[r, k], entrance_y[r, k] — grid coordinates for entrance k of room r
    # entrance_active[r, k] — binary: whether this entrance is used
    entrance_x = {}
    entrance_y = {}
    entrance_active = {}

    for r in rooms:
        for k in range(max_entrances_per_room):
            entrance_x[(r, k)] = solver.IntVar(0, building_width_in, f"door_x_{r}_{k}")
            entrance_y[(r, k)] = solver.IntVar(0, building_height_in, f"door_y_{r}_{k}")
            entrance_active[(r, k)] = solver.BoolVar(f"door_active_{r}_{k}")

    # -------------------------------
    # Constraints
    # -------------------------------

    # 1) Room must fit inside building shell
    add_room_bounds_constraints(
        solver, rooms, x, y, w, h, building_width_in, building_height_in
    )

    # 2) Ensure entrances lie on the room’s perimeter if active
    add_entry_bounds_constraints(
        solver, rooms, x, y, w, h, entrance_x, entrance_y, entrance_active
    )

    # 3) Non-overlap: rooms cannot overlap in interior (basic disjunctive constraints)
    add_non_overlap_constraints(solver, rooms, x, y, w, h)

    # 4) Simple example: for rooms that require entry from the clinical corridor
    #    We attach entrances to the corridor boundary. This is where ROOM_RULES entryRules
    #    will eventually drive which rooms get which constraints.
    if CLINICAL_CORRIDOR in rooms:
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
            corridor_room_id=CLINICAL_CORRIDOR,
        )

    # 5) Adjacency constraints based on ROOM_RULES["adjacencyRules"]
    add_adjacency_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES)

    # 6) Visibility constraints based on ROOM_RULES["visibilityRules"]
    add_visibility_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES)

    # -------------------------------
    # Objective (placeholder)
    # -------------------------------
    # Must be linear: no w[r] * h[r].
    # For now, minimize total (w + h) to mildly prefer smaller rooms.
    total_size = solver.Sum([w[r] + h[r] for r in rooms])
    solver.Minimize(total_size)

    vars_dict = {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "entrance_x": entrance_x,
        "entrance_y": entrance_y,
        "entrance_active": entrance_active,
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

    # List of room types we know about (from ruleset_consts)
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

    print("\nEnter desired count for each room type (0 for none).")
    print("NOTE: counts > 0 are currently treated as a single instance per type in this skeleton.\n")

    selected_rooms = []
    for rt in room_types:
        count = _prompt_nonnegative_int(f"{rt}: ")
        if count > 0:
            if rt not in ROOM_RULES:
                print(f"  [warning] No ROOM_RULES entry for '{rt}', it will have only generic constraints.")
            selected_rooms.append(rt)

    if not selected_rooms:
        print("No rooms selected (all counts were 0). Nothing to solve.")
        return

    solver, vars_dict = build_layout_model(
        building_width_in,
        building_height_in,
        selected_rooms,
    )

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print("\nFound layout (all dimensions in inches):")
        for r in selected_rooms:
            x_var = vars_dict["x"][r]
            y_var = vars_dict["y"][r]
            w_var = vars_dict["w"][r]
            h_var = vars_dict["h"][r]
            print(
                f"{r}: (x={x_var.solution_value():.0f}, "
                f"y={y_var.solution_value():.0f}, "
                f"w={w_var.solution_value():.0f}, "
                f"h={h_var.solution_value():.0f})"
            )
    else:
        print("No optimal solution found; status:", status)


if __name__ == "__main__":
    main()