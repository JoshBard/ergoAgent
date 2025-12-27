# layout_model.py
#
# Skeleton MIP layout model on a 1-inch discrete grid.
# - Rooms are axis-aligned rectangles with integer coordinates (x, y, w, h)
# - Entrances are discrete integer positions on the rectangle perimeter
# - Constraint details live in layout_constraints.py

from ortools.linear_solver import pywraplp # pyright: ignore[reportMissingImports]

from ..architecture.constraints import *
from ..architecture.room_rules import ROOM_RULES

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

    - building_width_in, building_height_in: total shell size in inches. Current iteration assumes rectangular shell
    - rooms: list of room INSTANCE identifiers (e.g., "TREATMENT_ROOM__0")
    - num_treatment_rooms: scalar used by tiered rules (sterilization)
    - max_entrances_per_room: maximum number of door locations we allow per room in v1
    - NOTE: CBC is linear solver only, constraints may have addition, multiplication by a constant, and logical evals
    Returns:
        solver, vars_dict
    """
    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("Could not create CBC solver")

    # -------------------------------
    # Variables
    # Every room is represented by vertex and dimension pairs
    # -------------------------------
    x = {}
    y = {}
    w = {}
    h = {}

    for r in rooms:
        x[r] = solver.IntVar(0, building_width_in, f"x_{r}")    # Args: (lower bound, upper bound, name)
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
    # Constraint functions do ROOM_RULES.get(r, {}) where r is the room INSTANCE id.
    # For multiple instances, build a rules dict keyed by instance id.
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

    # Corridor-specific constraints (pick the first corridor instance)
    corridor_instances = [r for r in rooms if r.split("__", 1)[0] == SPACE_ID.CLINICAL_CORRIDOR]
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

    add_adjacency_constraints_from_rules(
        solver, rooms, x, y, w, h
    )
    add_visibility_constraints_from_rules(
        solver, rooms, x, y, w, h
    )

    # Min constraints include a soft "prefer larger above min" reward;
    # no separate ideal-size objective is used.
    add_room_min_constraints_from_rules(
        solver, rooms, w, h, num_treatment_rooms
    )
    add_room_max_constraints_from_rules(
        solver, rooms, w, h, num_treatment_rooms
    )

    # -------------------------------
    # Objective
    # -------------------------------
    total_size = solver.Sum([w[r] + h[r] for r in rooms])
    solver.Maximize(total_size)

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

    #CLI interface for layout footprint
    print("Enter building shell size (inches).")

    building_width_in = _prompt_nonnegative_int("Building width in inches: ")
    building_height_in = _prompt_nonnegative_int("Building height in inches: ")

    if building_width_in <= 0 or building_height_in <= 0:
        print("Building dimensions must be positive.")
        return

    room_types = [
        r for r in SPACE_ID
        if r not in {
            SPACE_ID.MECHANICAL,
            SPACE_ID.STAFF_ENTRY,
        }
    ]
    
    # for testing we will focus on implementing pipeline in these rooms first
    test_room_types = [
        SPACE_ID.DOCTOR_OFFICE,
        SPACE_ID.STERILIZATION,
        SPACE_ID.PATIENT_RESTROOM,
        SPACE_ID.PATIENT_LOUNGE,
        SPACE_ID.CROSSOVER_HALLWAY,
        SPACE_ID.CLINICAL_CORRIDOR,
        SPACE_ID.TREATMENT_ROOM
    ]

    print("\nEnter desired count for each room type (0 for none).\n")

    selected_rooms = []
    counts_by_type = {}
    for rt in test_room_types:
        count = _prompt_nonnegative_int(f"{rt}: ")
        counts_by_type[rt] = count

        if count > 0 and rt not in ROOM_RULES:
            print(f"  [warning] No ROOM_RULES entry for '{rt}', it will have only generic constraints.")

        for i in range(count):
            selected_rooms.append(_make_instance_id(str(rt), i))

    if not selected_rooms:
        print("No rooms selected (all counts were 0). Nothing to solve.")
        return

    # Single treatment room type
    num_treatment_rooms = counts_by_type.get(SPACE_ID.TREATMENT_ROOM, 0)

    # Invoke builder, this sets solver constraints and defines variables
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
            x_val = vars_dict["x"][r].solution_value()
            y_val = vars_dict["y"][r].solution_value()
            w_val = vars_dict["w"][r].solution_value()
            h_val = vars_dict["h"][r].solution_value()
            
            # 1. Collect all active doors for this room
            active_doors = []
            # You need to know how many max_entrances there were (default was 2)
            for k in range(2): 
                door_var = vars_dict["entrance_active"].get((r, k))
                if door_var and door_var.solution_value() > 0.5: # 0.5 threshold for BoolVars
                    dx = vars_dict["entrance_x"][(r, k)].solution_value()
                    dy = vars_dict["entrance_y"][(r, k)].solution_value()
                    active_doors.append(f"Door_{k}@(x={dx:.0f}, y={dy:.0f})")

            base = r.split("__", 1)[0]
            doors_str = ", ".join(active_doors) if active_doors else "No active doors"
            
            print(
                f"{r} [{base}]: (x={x_val:.0f}, y={y_val:.0f}, w={w_val:.0f}, h={h_val:.0f}) | {doors_str}"
            )
    else:
        print("No optimal solution found; status:", status)


if __name__ == "__main__":
    main()
