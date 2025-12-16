# layout_constraints.py
#
# Constraint-building helpers for the rectangular grid model.
# All coordinates and lengths are discrete inches.


from ortools.linear_solver import pywraplp # pyright: ignore[reportMissingImports]

from ruleset_core import (
    RULE_ADJACENT,
    RULE_SEPARATE,
    RULE_ENTRY_FROM,
    RULE_ENTRY_NOT_FROM,
    RULE_ENTRY_WITHIN_DISTANCE,
    RULE_NEAR_SPACE,
    RULE_AVOID_VISIBILITY,
    RULE_REQUIRE_VISIBILITY,
    RULE_NOT_WITHIN_DISTANCE,
)


def add_room_bounds_constraints(
    solver, rooms, x, y, w, h, building_width_in, building_height_in
):
    """
    Ensure each room rectangle fits inside the building shell.
    """
    for r in rooms:
        # Right / top edges inside shell
        solver.Add(x[r] + w[r] <= building_width_in)
        solver.Add(y[r] + h[r] <= building_height_in)

        # Non-negative width/height (already enforced by domains, but keep semantics clear)
        solver.Add(w[r] >= 1)
        solver.Add(h[r] >= 1)


def add_non_overlap_constraints(solver, rooms, x, y, w, h):
    """
    Standard disjunctive non-overlap:
        For each pair of rooms i, j, one of:
            i is left of j
            i is right of j
            i is above j
            i is below j
    Uses big-M and 4 binaries per pair.
    """
    M = 10_000_000  # big enough upper bound for coordinate differences

    for i_idx in range(len(rooms)):
        for j_idx in range(i_idx + 1, len(rooms)):
            ri = rooms[i_idx]
            rj = rooms[j_idx]

            left = solver.BoolVar(f"{ri}_left_of_{rj}")
            right = solver.BoolVar(f"{ri}_right_of_{rj}")
            above = solver.BoolVar(f"{ri}_above_{rj}")
            below = solver.BoolVar(f"{ri}_below_{rj}")

            # At least one spatial relation must hold
            solver.Add(left + right + above + below >= 1)

            # If ri left of rj: x_i + w_i <= x_j
            solver.Add(x[ri] + w[ri] <= x[rj] + M * (1 - left))
            # If ri right of rj: x_j + w_j <= x_i
            solver.Add(x[rj] + w[rj] <= x[ri] + M * (1 - right))
            # If ri above rj: y_i >= y_j + h_j
            solver.Add(y[ri] >= y[rj] + h[rj] - M * (1 - above))
            # If ri below rj: y_j >= y_i + h_i
            solver.Add(y[rj] >= y[ri] + h[ri] - M * (1 - below))


def add_entry_bounds_constraints(
    solver, rooms, x, y, w, h, entrance_x, entrance_y, entrance_active
):
    """
    For each entrance (door) of each room, if active:
        - entrance must lie on the perimeter of the room rectangle.

    We'll use 4 binaries per entrance to select which side of the perimeter.
    """
    M = 10_000_000

    for (r, k), active_var in entrance_active.items():
        dx = entrance_x[(r, k)]
        dy = entrance_y[(r, k)]

        # Bound to building extents – already in variable domain, but repeat for clarity
        # (You can drop these lines if you set appropriate variable bounds)
        # solver.Add(dx >= 0)
        # solver.Add(dy >= 0)

        # Side selectors
        on_left = solver.BoolVar(f"door_{r}_{k}_on_left")
        on_right = solver.BoolVar(f"door_{r}_{k}_on_right")
        on_bottom = solver.BoolVar(f"door_{r}_{k}_on_bottom")
        on_top = solver.BoolVar(f"door_{r}_{k}_on_top")

        # If door is active, it must be on exactly one side
        solver.Add(on_left + on_right + on_bottom + on_top == active_var)

        # Side conditions (assuming active; relaxed by big-M when not on that side)
        # Left side: x = room.x, y within [room.y, room.y + h]
        solver.Add(dx - x[r] <= M * (1 - on_left))
        solver.Add(dx - x[r] >= -M * (1 - on_left))
        solver.Add(dy >= y[r] - M * (1 - on_left))
        solver.Add(dy <= y[r] + h[r] + M * (1 - on_left))

        # Right side: x = room.x + w
        solver.Add(dx - (x[r] + w[r]) <= M * (1 - on_right))
        solver.Add(dx - (x[r] + w[r]) >= -M * (1 - on_right))
        solver.Add(dy >= y[r] - M * (1 - on_right))
        solver.Add(dy <= y[r] + h[r] + M * (1 - on_right))

        # Bottom side: y = room.y
        solver.Add(dy - y[r] <= M * (1 - on_bottom))
        solver.Add(dy - y[r] >= -M * (1 - on_bottom))
        solver.Add(dx >= x[r] - M * (1 - on_bottom))
        solver.Add(dx <= x[r] + w[r] + M * (1 - on_bottom))

        # Top side: y = room.y + h
        solver.Add(dy - (y[r] + h[r]) <= M * (1 - on_top))
        solver.Add(dy - (y[r] + h[r]) >= -M * (1 - on_top))
        solver.Add(dx >= x[r] - M * (1 - on_top))
        solver.Add(dx <= x[r] + w[r] + M * (1 - on_top))


def add_simple_entry_from_corridor_constraints(
    solver,
    rooms,
    x,
    y,
    w,
    h,
    entrance_x,
    entrance_y,
    entrance_active,
    corridor_room_id,
):
    """
    Example constraint builder:
    For rooms that have an ENTRY_FROM rule pointing to the clinical corridor,
    we require at least one active entrance that lies on a shared boundary
    between the room and the corridor.

    This is a simple skeleton; you'll refine based on your door model.
    """
    if corridor_room_id not in rooms:
        return

    # Corridor rectangle
    x_c = x[corridor_room_id]
    y_c = y[corridor_room_id]
    w_c = w[corridor_room_id]
    h_c = h[corridor_room_id]

    # In a full implementation you’d inspect ROOM_RULES[r]["entryRules"]
    # Here we just show how to enforce "shared boundary" for a given pair.
    # TODO: call this only for rooms that actually require entry_from corridor.

    M = 10_000_000

    for r in rooms:
        if r == corridor_room_id:
            continue

        # require at least one entrance active IF the rules say so.
        # For now, we leave that conditional wiring as TODO and just
        # demonstrate how to enforce "if active, share boundary".
        # You’ll attach a binary “room_requires_corridor_entry[r]” later.
        # Here we assume they *may* have doors to corridor, but not required.

        # For each entrance, if it's active *and* is used as corridor entry:
        # - door coordinate must lie on both rectangles' perimeter
        # In practice you might add separate booleans per-door for
        # "this is the corridor door".
        for (room_id, k), active_var in entrance_active.items():
            if room_id != r:
                continue

            dx = entrance_x[(room_id, k)]
            dy = entrance_y[(room_id, k)]

            # Shared boundary means:
            # - door lies on room perimeter (already handled by add_entry_bounds_constraints)
            # - door also lies on corridor perimeter
            # We encode "if active, door is within corridor boundary band"
            solver.Add(dx >= x_c - M * (1 - active_var))
            solver.Add(dx <= x_c + w_c + M * (1 - active_var))
            solver.Add(dy >= y_c - M * (1 - active_var))
            solver.Add(dy <= y_c + h_c + M * (1 - active_var))

            # NOTE: This is still loose; to make it exact you'd also need
            # side-specific equality to corridor edges, similar to the room sides.


def add_adjacency_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES):
    """
    Parse ROOM_RULES[room]["adjacencyRules"] and add corresponding constraints.

    This is the dispatcher where your rule kinds (RULE_ADJACENT, RULE_SEPARATE, etc.)
    are turned into linear constraints.

    Currently implemented:
      - RULE_ADJACENT: require rectangles to touch along at least an edge
      - RULE_SEPARATE: forbid rectangles from touching (add minimum gap)

    Everything else is left as TODO / extension.
    """
    M = 10_000_000
    min_adjacent_overlap = 12  # one foot of overlap, arbitrary starter
    min_separation = 1         # at least 1 inch gap

    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        rules = spec.get("adjacencyRules", [])
        for rule in rules:
            kind = rule.get("kind")
            target = rule.get("space") or rule.get("target")
            hard = rule.get("hard", True)

            if target is None or target not in rooms:
                continue  # skip external/TBD references for now

            if kind == RULE_ADJACENT:
                # r must touch target along at least one edge, with some overlap.
                # We model "touch" via four possibilities, similar to non-overlap,
                # but forcing equality on one coordinate and overlap on the other.
                t = target

                # Four binaries: which side is touching
                touch_left = solver.BoolVar(f"{r}_touch_left_{t}")
                touch_right = solver.BoolVar(f"{r}_touch_right_{t}")
                touch_above = solver.BoolVar(f"{r}_touch_above_{t}")
                touch_below = solver.BoolVar(f"{r}_touch_below_{t}")

                # At least one side must be touching
                solver.Add(touch_left + touch_right + touch_above + touch_below >= 1)

                # Left: right edge of r equals left edge of t
                # and vertical overlap
                solver.Add(x[r] + w[r] == x[t] + M * (1 - touch_left))
                solver.Add(y[r] + min_adjacent_overlap <= y[t] + h[t] + M * (1 - touch_left))
                solver.Add(y[t] + min_adjacent_overlap <= y[r] + h[r] + M * (1 - touch_left))

                # Right: left edge of r equals right edge of t
                solver.Add(x[t] + w[t] == x[r] + M * (1 - touch_right))
                solver.Add(y[r] + min_adjacent_overlap <= y[t] + h[t] + M * (1 - touch_right))
                solver.Add(y[t] + min_adjacent_overlap <= y[r] + h[r] + M * (1 - touch_right))

                # Above: bottom of r equals top of t
                solver.Add(y[r] == y[t] + h[t] + M * (1 - touch_above))
                solver.Add(x[r] + min_adjacent_overlap <= x[t] + w[t] + M * (1 - touch_above))
                solver.Add(x[t] + min_adjacent_overlap <= x[r] + w[r] + M * (1 - touch_above))

                # Below: top of r equals bottom of t
                solver.Add(y[t] == y[r] + h[r] + M * (1 - touch_below))
                solver.Add(x[r] + min_adjacent_overlap <= x[t] + w[t] + M * (1 - touch_below))
                solver.Add(x[t] + min_adjacent_overlap <= x[r] + w[r] + M * (1 - touch_below))

                # NOTE: For soft adjacencies (hard=False) you would instead add
                # violation variables and penalize them in the objective.

            elif kind == RULE_SEPARATE:
                # r must not be adjacent to target; enforce a minimum gap.
                t = target

                # We can reuse the non-overlap pattern but push them apart by min_separation.
                # Equivalent to "rooms cannot even touch".
                # This is a simplified, always-hard version.
                sep_left = solver.BoolVar(f"{r}_sep_left_{t}")
                sep_right = solver.BoolVar(f"{r}_sep_right_{t}")
                sep_above = solver.BoolVar(f"{r}_sep_above_{t}")
                sep_below = solver.BoolVar(f"{r}_sep_below_{t}")

                solver.Add(sep_left + sep_right + sep_above + sep_below >= 1)

                # left: x_r + w_r + gap <= x_t
                solver.Add(x[r] + w[r] + min_separation <= x[t] + M * (1 - sep_left))
                # right: x_t + w_t + gap <= x_r
                solver.Add(x[t] + w[t] + min_separation <= x[r] + M * (1 - sep_right))
                # above: y_r >= y_t + h_t + gap
                solver.Add(y[r] >= y[t] + h[t] + min_separation - M * (1 - sep_above))
                # below: y_t >= y_r + h_r + gap
                solver.Add(y[t] >= y[r] + h[r] + min_separation - M * (1 - sep_below))

            else:
                # Other kinds: RULE_NEAR_SPACE, RULE_ENTRY_INTERNAL_CONNECTION, etc.
                # You’ll add specialized handlers for those later.
                continue


def add_visibility_constraints_from_rules(solver, rooms, x, y, w, h, ROOM_RULES):
    """
    Visibility skeleton.

    In a full model, visibility depends on line-of-sight, occlusion, and corridor positions.
    For now this is just a placeholder that shows where you'd plug in your logic based on:
      RULE_AVOID_VISIBILITY, RULE_REQUIRE_VISIBILITY, etc.
    """
    # In v1, you might skip actual visibility geometry and instead interpret
    # "avoid visibility" as "do not share a boundary" or "keep a minimum distance".
    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        rules = spec.get("visibilityRules", [])
        for rule in rules:
            kind = rule.get("kind")
            source = rule.get("source")
            hard = rule.get("hard", False)

            if source is None or source not in rooms:
                # If it's a group like PATIENT_VISUAL_ZONES, you'd have to expand it here.
                continue

            if kind == RULE_AVOID_VISIBILITY:
                # Simplified: treat as "separate_from" with a larger gap.
                # Real LOS modeling would be more complex.
                M = 10_000_000
                min_visibility_gap = 24  # 2 feet as arbitrary placeholder

                sep_left = solver.BoolVar(f"{r}_vis_sep_left_{source}")
                sep_right = solver.BoolVar(f"{r}_vis_sep_right_{source}")
                sep_above = solver.BoolVar(f"{r}_vis_sep_above_{source}")
                sep_below = solver.BoolVar(f"{r}_vis_sep_below_{source}")

                solver.Add(sep_left + sep_right + sep_above + sep_below >= 1)

                solver.Add(x[r] + w[r] + min_visibility_gap <= x[source] + M * (1 - sep_left))
                solver.Add(x[source] + w[source] + min_visibility_gap <= x[r] + M * (1 - sep_right))
                solver.Add(
                    y[r]
                    >= y[source] + h[source] + min_visibility_gap - M * (1 - sep_above)
                )
                solver.Add(
                    y[source]
                    >= y[r] + h[r] + min_visibility_gap - M * (1 - sep_below)
                )

            elif kind == RULE_REQUIRE_VISIBILITY:
                # Placeholder; you could require them to be on the same "front band"
                # or within some distance, depending on your visibility notion.
                # For now we do nothing and leave as TODO.
                pass
            else:
                continue

def add_room_min_constraints_from_rules(solver, rooms, w, h, num_treatment_rooms, ROOM_RULES):
    """
    Adds minimum width/height constraints based on ROOM_RULES[room]["dimensions"].

    Minimal policy: if there are multiple possible minima, we enforce the smallest feasible minimum
    (i.e., min width across options, min length across options). This avoids over-constraining v1.
    """
    def _safe_int(x):
        return x if isinstance(x, (int, float)) else None

    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        dims = spec.get("dimensions")

        # Skip unknown / TBD
        if dims is None or dims == "TBD":
            continue

        min_w = None
        min_h = None

        # Case 1: direct minimum/max format
        if isinstance(dims, dict) and isinstance(dims.get("minimum"), dict):
            mw = _safe_int(dims["minimum"].get("widthInches"))
            mh = _safe_int(dims["minimum"].get("lengthInches"))
            if mw is not None:
                min_w = mw if min_w is None else min(min_w, mw)
            if mh is not None:
                min_h = mh if min_h is None else min(min_h, mh)

        # Case 2: variants list, currently just take the minimum
        # TODO choose between variants, not just choose min
        if isinstance(dims, dict) and isinstance(dims.get("variants"), list):
            for v in dims["variants"]:
                if not isinstance(v, dict):
                    continue
                mw = _safe_int(v.get("widthInches"))
                mh = _safe_int(v.get("lengthInches"))
                if mw is not None:
                    min_w = mw if min_w is None else min(min_w, mw)
                if mh is not None:
                    min_h = mh if min_h is None else min(min_h, mh)

        # Case 3: minimumByOperators list
        # TODO pass in number of operators so it is not just outputting a min
        if isinstance(dims, dict) and isinstance(dims.get("minimumByOperators"), list):
            for row in dims["minimumByOperators"]:
                if not isinstance(row, dict):
                    continue
                mw = _safe_int(row.get("widthInches"))
                mh = _safe_int(row.get("lengthInches"))
                if mw is not None:
                    min_w = mw if min_w is None else min(min_w, mw)
                if mh is not None:
                    min_h = mh if min_h is None else min(min_h, mh)

        # Case 4: STERILIZATION handler
        # TODO does not handle longer axis for doors
        if (r == "STERILIZATION"):
            matched = None
            for _, tier in dims.items():
                tr_min = tier.get("treatmentRoomsMin")
                tr_max = tier.get("treatmentRoomsMax")
                if isinstance(tr_min, int) and isinstance(tr_max, int):
                    if tr_min <= num_treatment_rooms <= tr_max:
                        matched = tier
                        break

            if matched is not None:
                mw = matched.get("widthInches")
                ml = matched.get("lengthInches")
                if isinstance(mw, int):
                    solver.Add(w[r] >= mw)
                if isinstance(ml, int):
                    solver.Add(h[r] >= ml)
            else:
                # Safe fallback: enforce the smallest tier envelope
                tier_widths = []
                tier_lengths = []
                for _, tier in dims.items():
                    mw = tier.get("widthInches")
                    ml = tier.get("lengthInches")
                    if isinstance(mw, int):
                        tier_widths.append(mw)
                    if isinstance(ml, int):
                        tier_lengths.append(ml)

                if tier_widths:
                    solver.Add(w[r] >= min(tier_widths))
                if tier_lengths:
                    solver.Add(h[r] >= min(tier_lengths))


        # If we found anything, add constraints
        if min_w is not None:
            solver.Add(w[r] >= int(min_w))
        if min_h is not None:
            solver.Add(h[r] >= int(min_h))

def add_room_max_constraints_from_rules(solver, rooms, w, h, num_treatment_rooms, ROOM_RULES):
    """
    Hard UPPER bounds (maximum sizes) for each room, based on ROOM_RULES[*]["dimensions"].
    """
    def _safe_num(x):
        return x if isinstance(x, (int, float)) else None

    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        dims = spec.get("dimensions")
        if dims is None or dims == "TBD":
            continue

        max_w = None
        max_h = None

        # Case 1: direct maximum
        if isinstance(dims, dict) and isinstance(dims.get("maximum"), dict):
            mw = _safe_num(dims["maximum"].get("widthInches"))
            mh = _safe_num(dims["maximum"].get("lengthInches"))
            if mw is not None:
                max_w = mw if max_w is None else max(max_w, mw)
            if mh is not None:
                max_h = mh if max_h is None else max(max_h, mh)

        # Case 2: variants list -> max envelope
        # TODO just choosing max right
        if isinstance(dims, dict) and isinstance(dims.get("variants"), list):
            for v in dims["variants"]:
                if not isinstance(v, dict):
                    continue
                mw = _safe_num(v.get("widthInches"))
                mh = _safe_num(v.get("lengthInches"))
                if mw is not None:
                    max_w = mw if max_w is None else max(max_w, mw)
                if mh is not None:
                    max_h = mh if max_h is None else max(max_h, mh)

        # Case 4: STERILIZATION tier selection
        # TODO handle doorways
        # TODO can simplify because max and min are the same size
        if r == "STERILIZATION" and isinstance(dims, dict):
            matched = None
            for _, tier in dims.items():
                if not isinstance(tier, dict):
                    continue
                tr_min = tier.get("treatmentRoomsMin")
                tr_max = tier.get("treatmentRoomsMax")
                if isinstance(tr_min, int) and isinstance(tr_max, int) and tr_min <= num_treatment_rooms <= tr_max:
                    matched = tier
                    break

            if matched is not None:
                mw = matched.get("widthInches")
                ml = matched.get("lengthInches")
                if isinstance(mw, int):
                    max_w = mw if max_w is None else min(max_w, mw)
                if isinstance(ml, int):
                    max_h = ml if max_h is None else min(max_h, ml)
            else:
                tier_widths = []
                tier_lengths = []
                for _, tier in dims.items():
                    if not isinstance(tier, dict):
                        continue
                    mw = tier.get("widthInches")
                    ml = tier.get("lengthInches")
                    if isinstance(mw, int):
                        tier_widths.append(mw)
                    if isinstance(ml, int):
                        tier_lengths.append(ml)
                # fallback: max envelope across tiers
                if tier_widths:
                    max_w = max(tier_widths) if max_w is None else min(max_w, max(tier_widths))
                if tier_lengths:
                    max_h = max(tier_lengths) if max_h is None else min(max_h, max(tier_lengths))

        if max_w is not None:
            solver.Add(w[r] <= int(max_w))
        if max_h is not None:
            solver.Add(h[r] <= int(max_h))


def add_room_ideal_size_soft_objective(solver, rooms, w, h, ROOM_RULES, weight=1.0):
    """
    Soft preference toward ideal sizes.

    TODO uses a linear penalty, may need to change
    """
    def _safe_num(x):
        return x if isinstance(x, (int, float)) else None

    penalties = []
    penalty_vars = []

    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        dims = spec.get("dimensions")
        if not (isinstance(dims, dict) and isinstance(dims.get("ideal"), dict)):
            continue

        ideal_w = _safe_num(dims["ideal"].get("widthInches"))
        ideal_h = _safe_num(dims["ideal"].get("lengthInches"))
        if ideal_w is None and ideal_h is None:
            continue

        # Linearize abs(w - ideal_w)
        if ideal_w is not None:
            dw_pos = solver.NumVar(0, solver.infinity(), f"{r}_ideal_w_pos")
            dw_neg = solver.NumVar(0, solver.infinity(), f"{r}_ideal_w_neg")
            solver.Add(w[r] - ideal_w == dw_pos - dw_neg)
            penalties.append(dw_pos)
            penalties.append(dw_neg)
            penalty_vars.extend([dw_pos, dw_neg])

        # Linearize abs(h - ideal_h)
        if ideal_h is not None:
            dh_pos = solver.NumVar(0, solver.infinity(), f"{r}_ideal_h_pos")
            dh_neg = solver.NumVar(0, solver.infinity(), f"{r}_ideal_h_neg")
            solver.Add(h[r] - ideal_h == dh_pos - dh_neg)
            penalties.append(dh_pos)
            penalties.append(dh_neg)
            penalty_vars.extend([dh_pos, dh_neg])

    if not penalties:
        return 0, []

    return weight * solver.Sum(penalties), penalty_vars