Step 1 — Stop the “1x1 inch room” degeneracy
1.1 Add a size constraint builder (DONE)

File: layout_constraints.py
Add near the top (right after imports), a new function:

add_room_min_size_constraints_from_rules(solver, rooms, w, h, ROOM_RULES)

What it should do:

For each room r, read ROOM_RULES[r]["dimensions"]

Pick a minimum width/length rule to enforce (MVP: use dimensions["minimum"] if present; else if minimumByOperators exists pick the smallest; else if variants exists pick the smallest; else skip if "TBD").

Add:

solver.Add(w[r] >= min_width)

solver.Add(h[r] >= min_length)

1.2 Wire it into the model (DONE)

File: layout_model.py
After add_room_bounds_constraints(...) call, add:

add_room_min_size_constraints_from_rules(solver, rooms, w, h, ROOM_RULES)

Also add the import at top:

from layout_constraints import add_room_min_size_constraints_from_rules

Step 2 — Make entry counts real (not optional binaries forever)
2.1 Add entry count constraints from rules

File: layout_constraints.py
Add function:

add_entry_count_constraints_from_rules(solver, rooms, entrance_active, ROOM_RULES, inputs=None)

Behavior:

For each room r:

Look at ROOM_RULES[r].get("entries")

If it has:

"minEntries": enforce Sum_k entrance_active[r,k] >= minEntries

"maxEntries": enforce <= maxEntries

"allowedEntryCounts": enforce membership (MVP: if allowed is [1,2], just enforce between 1 and 2; later you can do exact membership with binaries)

"byTreatmentRooms": this depends on a user input (treatment room count). For now:

Either pass inputs["treatmentRooms"] into the function and select the correct tier

Or skip (but at least you support the constant min/max cases)

2.2 Wire it into the model

File: layout_model.py
Right after add_entry_bounds_constraints(...), call:

add_entry_count_constraints_from_rules(solver, rooms, entrance_active, ROOM_RULES, inputs=inputs)

You’ll need to:

Add inputs param to build_layout_model(...)

Pass it from main() (even if empty)

Step 3 — Replace the corridor-door “bounding box” hack with actual shared-boundary logic

Right now you do: “door point inside corridor rectangle” which is not “door connects to corridor”.

3.1 Implement a shared-boundary primitive

File: layout_constraints.py
Add helper:

add_shared_boundary_door_constraint(solver, r, t, x, y, w, h, dx, dy, active, M)

This should enforce: if active, then door point is on the perimeter of BOTH rectangles, and in the same coordinate (shared edge).

MVP approach:

You already force door on room perimeter in add_entry_bounds_constraints.

So here, only force door on target perimeter, same pattern:

door on left edge of target OR right edge OR top OR bottom (4 binaries tied to active)

plus “within span” constraints

This is still not “shared edge” but “door on target perimeter”. To make it truly shared:

Add equalities linking the relevant edge coordinate of room and target:

Example: if door is on target left edge, also require dx == x[t] and dx == x[r] + w[r] (or dx == x[r]) depending on which room edge it’s on.

MVP compromise (still useful): door must be on both perimeters; that forces them to touch at that point.

3.2 Replace add_simple_entry_from_corridor_constraints with a rules-driven version

File: layout_constraints.py
Either delete or leave the old function and add a new one:

add_entry_constraints_from_rules(solver, rooms, x, y, w, h, entrance_x, entrance_y, entrance_active, ROOM_RULES)

This becomes your dispatcher for entry rules:

For each room r:

For each entry rule in ROOM_RULES[r]["entryRules"]:

RULE_ENTRY_FROM:

require at least one door connects to that space

implement by creating binary door_connects[r,k,target] and:

door_connects <= entrance_active

if door_connects == 1, apply shared-boundary door constraint

then enforce Sum_k door_connects[r,k,target] >= 1 (hard rules only)

RULE_ENTRY_NOT_FROM:

forbid any door connecting to that space:

Sum_k door_connects[r,k,target] == 0

RULE_ENTRY_FROM_ONE_OF:

require at least one door connects to any of the allowed spaces:

Sum_{k,target in set} door_connects[...] >= 1

RULE_ENTRY_WITHIN_DISTANCE:

MVP: door point within distance to target rectangle

Implement Manhattan distance with extra vars (see Step 5)

RULE_NOT_FROM_ANY_OTHER_ROOM_INTERIOR:

MVP: door may only connect to a set (e.g., corridor, lobby). You decide the allowed set.

Encode by requiring all door_connects[r,k,otherRoom] == 0 for disallowed rooms.

3.3 Wire it in

File: layout_model.py

Remove (or keep but stop calling) add_simple_entry_from_corridor_constraints

Add call after entry bounds/counts:

add_entry_constraints_from_rules(...)

Step 4 — Make the adjacency dispatcher cover your real rules
4.1 Add near-distance (RULE_NEAR_SPACE)

File: layout_constraints.py

Inside add_adjacency_constraints_from_rules(...), add handling for:

RULE_NEAR_SPACE

Implementation MVP:

Define a function rect_manhattan_distance(...) (Step 5) returning a linear var dist.

If hard: solver.Add(dist <= maxDistanceInches)

If soft: create violation >= dist - maxDistance, violation >= 0 and return it for objective (Step 6)

4.2 Add not-within-distance (RULE_NOT_WITHIN_DISTANCE)

Same pattern, hard:

solver.Add(dist >= minDistanceInches)

Soft:

violation >= minDistance - dist, violation >= 0

4.3 Add “prefer near center” semantics

Add handlers for:

RULE_PREFER_NEAR_CLINICAL_CENTER

RULE_PREFER_NEAR_TREATMENT_CENTER

MVP definition you can actually encode now:

Clinical center = center of CLINICAL_CORRIDOR rectangle (if present)

Treatment center = average center of all treatment rooms present (harder). MVP: just use corridor center too.

Create:

cx_r = x[r] + w[r]/2 is not linear if /2 on int vars is annoying; use:

cx2_r = 2*x[r] + w[r] (this equals 2*center_x)

same for y
Then use Manhattan distance on these doubled centers.

Make them soft penalties only.

Step 5 — Add a reusable “Manhattan distance between rectangles” primitive (linear)

You need this for near/within/not-within and later for “visibility proxy”.

5.1 Add this helper

File: layout_constraints.py

Add:

add_rect_manhattan_distance_vars(solver, x1, y1, w1, h1, x2, y2, w2, h2, name_prefix)

Return a dict with:

dx_pos, dx_neg, dy_pos, dy_neg, dist
Where:

dx_pos >= (x2 - (x1 + w1)) (gap if 2 is to the right)

dx_pos >= 0

dx_neg >= (x1 - (x2 + w2)) (gap if 1 is to the right)

dx_neg >= 0

Similarly for y gaps
Then:

dist = dx_pos + dx_neg + dy_pos + dy_neg

This yields 0 if rectangles overlap or touch in either axis; positive if separated.

Use this everywhere you currently use vague proximity.

Step 6 — Introduce a real objective with soft penalties
6.1 Make constraints return penalty vars

File: layout_constraints.py

Change:

add_adjacency_constraints_from_rules(...) to optionally collect and return a list of penalty vars.

Example:

return penalty_vars

For each soft rule (where hard=False):

Create a violation IntVar(0, big, ...)

Add constraints linking it to the distance or separation

Append (violation, weight) or store weight elsewhere

6.2 Wire into layout_model.py

In build_layout_model(...):

Create penalties = []

Collect penalties from:

adjacency dispatcher

entry-within-distance dispatcher

visibility dispatcher (proxy)

Objective:

solver.Minimize( solver.Sum([weight * v for (v, weight) in penalties]) + tiny_size_term )

Keep the tiny size term as a tie-breaker:

0.001*(w+h) is not allowed in integer solver directly; instead scale:

1000*penalties + 1*(w+h) style

Step 7 — Support counts (multiple instances per type)

This is the biggest structural jump, but you’ll need it.

7.1 Expand selected rooms into instances

File: layout_model.py

In main(), you currently build selected_rooms as a list of types. Change to:

selected_instances = []

for each room type rt and user count c:

for i in range(c):

selected_instances.append((rt, i))

Then the model variables become keyed by instance id:

x[(rt,i)], w[(rt,i)], etc.

7.2 Teach the rule compiler how to interpret rules with instances

Rules reference room types (e.g., CONSULT), but you now have many consult instances.
When you see a target CONSULT, expand it to “all instances of that type”.

So in constraint dispatchers:

build a helper map:

instances_by_type: dict[type -> list[instanceId]]

Then:

direct_adjacency(CLINICAL_CORRIDOR) means: must be adjacent to the corridor instance(s) (often 1)

separate_from(PATIENT_LOUNGE) means: separate from all patient lounge instances (likely 1)

near_space(CHECK_OUT) etc.

Step 8 — Clean up remaining string placeholders in rules

Right now you still have strings like "waitingRoom", "entry", "restrooms", "staffCorridor", "treatmentRoom".

8.1 Decide which ones become constants vs skipped

File: ruleset_consts.py

Add missing identifiers you plan to model as rectangles:

WAITING_ROOM (or just use PATIENT_LOUNGE)

ENTRY_VESTIBULE

STAFF_CORRIDOR

SECOND_CROSSOVER_HALLWAY (if you want it as a room)

If you don’t want to model them now:

Keep them as "TBD"-style and make the dispatcher explicitly skip targets not present.