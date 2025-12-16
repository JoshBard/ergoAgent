# layout_constraints.py
#
# Constraint-building helpers for the rectangular grid model.
# All coordinates and lengths are discrete inches.


from ortools.linear_solver import pywraplp # pyright: ignore[reportMissingImports]
from core import *
import room_rules as ROOM_RULES

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


def add_adjacency_constraints_from_rules(solver, rooms, x, y, w, h):
    """
    DIRECT adjacency (hard, non-negotiable):
      - exactly WALL_THICKNESS inches between room envelopes on one of 4 sides
      - AND at least min_adjacent_overlap inches of overlap on the perpendicular axis
        (this is wall-segment overlap, NOT area overlap)

    separation:
      - min gap (no touching)

    preferredProximity:
      - soft objective (optional hard cap)

    Also: DIRECT adjacency constraints are added only once per unordered pair (r,t),
    to avoid duplicating constraints when rules exist in both directions.
    """
    M = 10_000_000
    WALL_THICKNESS = 12        # inches between adjacent room envelopes
    min_adjacent_overlap = 24  # inches of shared wall segment required
    min_separation = 180        # inches: separation rules (cannot even touch)
    # TODO make the separation logic clear. right now we just account for a room between them with 15 feet of space, does not have any notion of rooms between them

    # ----------------------------
    # Helpers
    # ----------------------------
    def _room_category(rid):
        return ROOM_RULES.get(rid, {}).get("identity", {}).get("category", None)

    def _rooms_in_group(group):
        # Default grouping; swap out later if you add explicit memberships.
        if group == SPACE_GROUP.CLINICAL:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.CLINICAL}
        if group == SPACE_GROUP.PUBLIC:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PUBLIC}
        if group == SPACE_GROUP.PRIVATE:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PRIVATE}
        if group == SPACE_GROUP.CORRIDORS:
            # Prefer explicit SPACE_IDs for corridors; this is only a fallback.
            return {r for r in rooms if "CORRIDOR" in str(r) or "HALLWAY" in str(r)}
        if group == SPACE_GROUP.PATIENT_FACING:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PUBLIC}
        return set()

    def _resolve_targets(target):
        if target is None:
            return []
        if isinstance(target, SPACE_ID):
            return [target] if target in rooms else []
        if isinstance(target, SPACE_GROUP):
            return [t for t in _rooms_in_group(target) if t in rooms]
        return []

    def _objective():
        return solver.Objective()

    def _penalize(var, weight):
        if weight is None or weight <= 0:
            return
        _objective().SetCoefficient(var, float(weight))
        _objective().SetMinimization()

    def _manhattan_dist(a, b, name):
        dx = solver.NumVar(0, solver.infinity(), f"{name}_dx")
        dy = solver.NumVar(0, solver.infinity(), f"{name}_dy")
        solver.Add(dx >= x[a] - x[b])
        solver.Add(dx >= x[b] - x[a])
        solver.Add(dy >= y[a] - y[b])
        solver.Add(dy >= y[b] - y[a])
        d = solver.NumVar(0, solver.infinity(), f"{name}_dman")
        solver.Add(d == dx + dy)
        return d

    def _pair_key(a, b):
        # stable unordered key for Enum values
        return (a.name, b.name) if a.name < b.name else (b.name, a.name)

    # Track which direct adjacency pairs we've already constrained
    seen_direct_pairs = set()

    # ----------------------------
    # Main loop
    # ----------------------------
    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        adj = spec.get("adjacency", {}) or {}

        direct_rules = adj.get("direct", []) or []
        sep_rules = adj.get("separation", []) or []
        prox_rules = adj.get("preferredProximity", []) or []

        # ---- DIRECT: fixed wall + shared wall segment overlap (once per pair) ----
        for rule in direct_rules:
            target = rule.get("target")
            for t in _resolve_targets(target):
                if t == r:
                    continue

                key = _pair_key(r, t)
                if key in seen_direct_pairs:
                    continue
                seen_direct_pairs.add(key)

                left  = solver.BoolVar(f"{r}_adj_left_{t}")
                right = solver.BoolVar(f"{r}_adj_right_{t}")
                above = solver.BoolVar(f"{r}_adj_above_{t}")
                below = solver.BoolVar(f"{r}_adj_below_{t}")

                # Must pick at least one adjacency side
                solver.Add(left + right + above + below >= 1)

                # LEFT: r is left of t (vertical shared wall segment)
                solver.Add(x[r] + w[r] + WALL_THICKNESS == x[t] + M * (1 - left))
                solver.Add(y[r] + min_adjacent_overlap <= y[t] + h[t] + M * (1 - left))
                solver.Add(y[t] + min_adjacent_overlap <= y[r] + h[r] + M * (1 - left))

                # RIGHT: r is right of t
                solver.Add(x[t] + w[t] + WALL_THICKNESS == x[r] + M * (1 - right))
                solver.Add(y[r] + min_adjacent_overlap <= y[t] + h[t] + M * (1 - right))
                solver.Add(y[t] + min_adjacent_overlap <= y[r] + h[r] + M * (1 - right))

                # ABOVE: r is above t (horizontal shared wall segment)
                solver.Add(y[t] + h[t] + WALL_THICKNESS == y[r] + M * (1 - above))
                solver.Add(x[r] + min_adjacent_overlap <= x[t] + w[t] + M * (1 - above))
                solver.Add(x[t] + min_adjacent_overlap <= x[r] + w[r] + M * (1 - above))

                # BELOW: r is below t
                solver.Add(y[r] + h[r] + WALL_THICKNESS == y[t] + M * (1 - below))
                solver.Add(x[r] + min_adjacent_overlap <= x[t] + w[t] + M * (1 - below))
                solver.Add(x[t] + min_adjacent_overlap <= x[r] + w[r] + M * (1 - below))

        # ---- SEPARATION: min gap (no touching) ----
        for rule in sep_rules:
            target = rule.get("target")
            hard = bool(rule.get("hard", True))
            if not hard:
                # schema allows soft, but you can extend later; currently treat as hard
                pass

            for t in _resolve_targets(target):
                if t == r:
                    continue

                sep_left  = solver.BoolVar(f"{r}_sep_left_{t}")
                sep_right = solver.BoolVar(f"{r}_sep_right_{t}")
                sep_above = solver.BoolVar(f"{r}_sep_above_{t}")
                sep_below = solver.BoolVar(f"{r}_sep_below_{t}")

                solver.Add(sep_left + sep_right + sep_above + sep_below >= 1)

                solver.Add(x[r] + w[r] + min_separation <= x[t] + M * (1 - sep_left))
                solver.Add(x[t] + w[t] + min_separation <= x[r] + M * (1 - sep_right))
                solver.Add(y[r] >= y[t] + h[t] + min_separation - M * (1 - sep_above))
                solver.Add(y[t] >= y[r] + h[r] + min_separation - M * (1 - sep_below))

        # ---- PREFERRED PROXIMITY: objective + optional cap ----
        for rule in prox_rules:
            target = rule.get("target")
            max_dist = rule.get("maxDistanceInches")
            weight = float(rule.get("optimizationWeight", 0.0) or 0.0)

            for t in _resolve_targets(target):
                if t == r:
                    continue

                d = _manhattan_dist(r, t, name=f"{r}_prox_{t}")
                if max_dist is not None:
                    solver.Add(d <= int(max_dist))
                _penalize(d, weight=weight)

def add_visibility_constraints_from_rules(solver, rooms, x, y, w, h):
    """
    Schema-based visibility:

      ROOM_RULES[room]["visibility"]["mustBeHiddenFrom"] -> enforce separation with a visibility gap
      ROOM_RULES[room]["visibility"]["mustBeVisibleFrom"] -> enforce proximity (placeholder)

    NOTE (v1):
      We are NOT doing true line-of-sight / occlusion.
      - "Hidden" is approximated as: keep at least `min_visibility_gap` inches apart in x OR y.
      - "Visible" is approximated as: keep within `max_visibility_dist` (Manhattan), optionally.

    TODO get a notion of doorway visibility through corridors and hallway
    """
    M = 10_000_000

    # You can tune these as global defaults for v1.
    min_visibility_gap = 180      # minimum to be invisible
    max_visibility_dist = 120    # maximum to be visible

    # ----------------------------
    # Helpers
    # ----------------------------
    def _room_category(rid):
        return ROOM_RULES.get(rid, {}).get("identity", {}).get("category", None)

    def _rooms_in_group(group):
        if group == SPACE_GROUP.CLINICAL:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.CLINICAL}
        if group == SPACE_GROUP.PUBLIC:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PUBLIC}
        if group == SPACE_GROUP.PRIVATE:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PRIVATE}
        if group == SPACE_GROUP.CORRIDORS:
            return {r for r in rooms if "CORRIDOR" in str(r) or "HALLWAY" in str(r)}
        if group == SPACE_GROUP.PATIENT_FACING:
            return {r for r in rooms if _room_category(r) == ROOM_CATEGORY.PUBLIC}
        return set()

    def _resolve_targets(target):
        if target is None:
            return []
        if isinstance(target, SPACE_ID):
            return [target] if target in rooms else []
        if isinstance(target, SPACE_GROUP):
            return [t for t in _rooms_in_group(target) if t in rooms]
        return []

    def _manhattan_dist(a, b, name):
        dx = solver.NumVar(0, solver.infinity(), f"{name}_dx")
        dy = solver.NumVar(0, solver.infinity(), f"{name}_dy")
        solver.Add(dx >= x[a] - x[b])
        solver.Add(dx >= x[b] - x[a])
        solver.Add(dy >= y[a] - y[b])
        solver.Add(dy >= y[b] - y[a])
        d = solver.NumVar(0, solver.infinity(), f"{name}_dman")
        solver.Add(d == dx + dy)
        return d

    def _pair_key(a, b):
        return (a.name, b.name) if a.name < b.name else (b.name, a.name)

    seen_hidden_pairs = set()
    seen_visible_pairs = set()

    # ----------------------------
    # Main loop
    # ----------------------------
    for r in rooms:
        spec = ROOM_RULES.get(r, {})
        vis = spec.get("visibility", {}) or {}

        hidden_rules = vis.get("mustBeHiddenFrom", []) or []
        visible_rules = vis.get("mustBeVisibleFrom", []) or []

        # ---- MUST BE HIDDEN FROM: enforce separation gap ----
        for rule in hidden_rules:
            target = rule.get("target")
            hard = bool(rule.get("hard", True))
            # v1: treat as hard only; skip soft for now
            if not hard:
                continue

            for t in _resolve_targets(target):
                if t == r:
                    continue

                key = _pair_key(r, t)
                if key in seen_hidden_pairs:
                    continue
                seen_hidden_pairs.add(key)

                # Enforce: r and t are separated by at least min_visibility_gap in x OR y
                sep_left  = solver.BoolVar(f"{r}_vis_hide_left_{t}")
                sep_right = solver.BoolVar(f"{r}_vis_hide_right_{t}")
                sep_above = solver.BoolVar(f"{r}_vis_hide_above_{t}")
                sep_below = solver.BoolVar(f"{r}_vis_hide_below_{t}")

                solver.Add(sep_left + sep_right + sep_above + sep_below >= 1)

                solver.Add(x[r] + w[r] + min_visibility_gap <= x[t] + M * (1 - sep_left))
                solver.Add(x[t] + w[t] + min_visibility_gap <= x[r] + M * (1 - sep_right))
                solver.Add(y[r] >= y[t] + h[t] + min_visibility_gap - M * (1 - sep_above))
                solver.Add(y[t] >= y[r] + h[r] + min_visibility_gap - M * (1 - sep_below))

        # ---- MUST BE VISIBLE FROM: simple proximity placeholder ----
        for rule in visible_rules:
            target = rule.get("target")
            hard = bool(rule.get("hard", True))
            if not hard:
                continue

            for t in _resolve_targets(target):
                if t == r:
                    continue

                key = _pair_key(r, t)
                if key in seen_visible_pairs:
                    continue
                seen_visible_pairs.add(key)

                # Placeholder: require them to be within some Manhattan distance.
                # Replace with corridor/LOS logic later.
                d = _manhattan_dist(r, t, name=f"{r}_vis_req_{t}")
                solver.Add(d <= max_visibility_dist)

def add_room_min_constraints_from_rules(solver, rooms, w, h, num_treatment_rooms):
    """
    HARD mins from ROOM_RULES[r]["geometry"]["dimensionModels"], but instead of "pick one model",
    we:

      1) Compute the minimum required width/length from the *applicable* option set
         (matching TR-tier if available; else generic; else all).
      2) Enforce w[r] >= min_w and h[r] >= min_h
      3) Add an objective term that *rewards being larger* (equivalently: penalizes being smaller),
         while still respecting the min constraints.

    # TODO currently penalizing smaller rooms, this may need to change
    # TODO add a trigger for rooms that need to be cognizant of treatments room etc. then check those specifically here instead of all
    """
    SIZE_REWARD = 1e-3  # small: increase if you want “bigger rooms” to matter more

    def _matches_tr(m):
        tr_min = m.get("treatmentRoomsMin")
        tr_max = m.get("treatmentRoomsMax")
        if tr_min is None and tr_max is None:
            return None  # generic
        if isinstance(tr_min, int) and isinstance(tr_max, int):
            return tr_min <= num_treatment_rooms <= tr_max
        if isinstance(tr_min, int) and tr_max is None:
            return num_treatment_rooms >= tr_min
        if tr_min is None and isinstance(tr_max, int):
            return num_treatment_rooms <= tr_max
        return False

    obj = solver.Objective()
    obj.SetMinimization()

    for r in rooms:
        models = (ROOM_RULES.get(r, {}).get("geometry", {}) or {}).get("dimensionModels", []) or []
        models = [m for m in models if isinstance(m, dict)]
        if not models:
            continue

        matching = [m for m in models if _matches_tr(m) is True]
        generic = [m for m in models if _matches_tr(m) is None]

        # Applicable set: prefer matching tier, else generic, else all
        candidates = matching or generic or models

        widths = [m.get("widthInches") for m in candidates if isinstance(m.get("widthInches"), int)]
        lengths = [m.get("lengthInches") for m in candidates if isinstance(m.get("lengthInches"), int)]

        min_w = min(widths) if widths else None
        min_h = min(lengths) if lengths else None

        if min_w is not None:
            solver.Add(w[r] >= min_w)
            # reward being larger than min by rewarding w itself (constant min doesn't matter)
            obj.SetCoefficient(w[r], obj.GetCoefficient(w[r]) - SIZE_REWARD)

        if min_h is not None:
            solver.Add(h[r] >= min_h)
            obj.SetCoefficient(h[r], obj.GetCoefficient(h[r]) - SIZE_REWARD)



def add_room_max_constraints_from_rules(solver, rooms, w, h, num_treatment_rooms):
    """
    HARD max bounds from ROOM_RULES[r]["geometry"]["dimensionModels"].

    Uses the SAME selection rule as min (choose largest relevant envelope),
    then enforces:
      w[r] <= chosen.widthInches
      h[r] <= chosen.lengthInches

    This makes width/length effectively FIXED to the chosen envelope if both exist.
    """
    def _matches_tr(m):
        tr_min = m.get("treatmentRoomsMin")
        tr_max = m.get("treatmentRoomsMax")
        if tr_min is None and tr_max is None:
            return None  # generic
        if isinstance(tr_min, int) and isinstance(tr_max, int):
            return tr_min <= num_treatment_rooms <= tr_max
        if isinstance(tr_min, int) and tr_max is None:
            return num_treatment_rooms >= tr_min
        if tr_min is None and isinstance(tr_max, int):
            return num_treatment_rooms <= tr_max
        return False

    def _score(m):
        wi = m.get("widthInches")
        li = m.get("lengthInches")
        wi = wi if isinstance(wi, int) else 0
        li = li if isinstance(li, int) else 0
        return (wi, li, wi * li)

    for r in rooms:
        models = (ROOM_RULES.get(r, {}).get("geometry", {}) or {}).get("dimensionModels", []) or []
        models = [m for m in models if isinstance(m, dict)]
        if not models:
            continue

        matching = [m for m in models if _matches_tr(m) is True]
        generic = [m for m in models if _matches_tr(m) is None]

        if matching:
            chosen = max(matching, key=_score)
        elif generic:
            chosen = max(generic, key=_score)
        else:
            chosen = max(models, key=_score)

        wi = chosen.get("widthInches")
        li = chosen.get("lengthInches")

        if isinstance(wi, int):
            solver.Add(w[r] <= wi)
        if isinstance(li, int):
            solver.Add(h[r] <= li)

# TODO add an ideal penalty for size of treatmeant rooms when we are ready to address those specifically