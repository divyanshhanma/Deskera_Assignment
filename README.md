# ERP.AI Engineering Assessment – Part 2

This document outlines the design and implementation choices for the **Factory Steady State** and **Bounded Belts** problems.

---

## Factory Modeling Choices

### Item balances and conservation

The Factory steady-state model uses a variable `x_r` (crafts per minute) for each recipe `r`.

For each item `i`, the conservation equation is:

```
sum_r ( out_r[i] * (1 + prod_m) * x_r ) 
  - sum_r ( in_r[i] * x_r ) 
  = b[i]
```

Interpretation:

- **Target item `t`** → `b[t] = target_rate`
- **Intermediate items** → `b[i] = 0` (production = consumption)
- **Raw items** → `b[i] <= 0` and `|b[i]| <= raw_cap[i]`

---

### Raw consumption & machine capacity

Raw consumption constraint (per raw item `j`):

```
sum_r ( in_r[j] * x_r ) <= raw_cap[j]
```

Machine throughput:

```
eff_crafts_per_min(r) = machines[m].crafts_per_min 
                        * (1 + speed) 
                        * 60 / time_s(r)
```

Machine usage:

```
machines_used_by_r = x_r / eff_crafts_per_min(r)
```

Constraint:

```
sum_{recipes using m} machines_used_by_r <= max_machines[m]
```

---

### Module Application

- Modules apply **per machine type**
- `speed` → multiplies machine crafting rate  
- `prod` → multiplies **only outputs** of recipes

---

### Cycles, Byproducts, and Self-Contained Recipes

Handled automatically via:

- Balanced internal items: `b[i] = 0`
- LP solver determines any cyclic steady-state

---

### Tie-breaking (min machines)

Secondary objective: minimize total machines.

```
minimize  Σ_m Σ_r ( x_r / eff_crafts_per_min(r) )
```

---

### Infeasibility Reporting

If full target is not feasible:

- Binary search on target rate  
- For maximum feasible rate → report:
  - `max_feasible_rate`
  - bottleneck hints (via LP duals)

---

## Belts Modeling Choices

### Max-flow with lower bounds

The Bounded Belts problem is modeled using:

- Lower-bound flow transformation  
- Node-splitting for capacities  
- Feasibility check via super-source/sink  

---

### Step 1: Node splitting (for node caps)

For each capped node `v`:

- Split into `v_in → v_out` with capacity = node cap  
- Incoming edges → `v_in`  
- Outgoing edges → `v_out`

---

### Step 2: Lower bound edge transformation

For edge `(u → v)` with `lo`, `hi`:

- Replace capacity with `hi - lo`
- Adjust demands:  
  - `demand[v] += lo`  
  - `demand[u] -= lo`
- Add `lo` back after solving

---

### Feasibility Check

Add super-source `s*` and super-sink `t*`.

If max-flow saturates all edges from `s*`, then feasible.

Otherwise:

- System is **infeasible**
- Min-cut gives:
  - reachable nodes
  - deficit
  - tight nodes and edges

---

## Numeric Approach

- Floating-point tolerance: `1e-9`
- **Factory** uses Linear Programming (PuLP / linprog)
- **Belts** uses Dinic / Edmonds-Karp
- Deterministic tie-breaking using sorted names

---

## Failure Modes & Edge Cases

### Factory

- Cycles → handled by LP
- Machine/raw shortages → infeasible → binary search
- Redundant recipes → deterministic selection

### Belts

- Disconnected components → 0 flow
- Zero capacity edges → handled by transformations

---

## Input / Output — Exact JSON Formats

Both tools use **JSON on stdin and stdout**.

---

### Factory Input (stdin)

```json
{
  "machines": { machine_name: { "crafts_per_min": number } },
  "recipes": {
    recipe_name: {
      "machine": "name",
      "time_s": number,
      "in": { item: qty },
      "out": { item: qty }
    }
  },
  "modules": { machine_name: { "prod": number, "speed": number } },
  "limits": {
    "raw_supply_per_min": { item: cap },
    "max_machines": { machine: cap }
  },
  "target": { "item": "name", "rate_per_min": number }
}
```

---

### Factory Output (stdout)

### If feasible:

```json
{
  "status": "ok",
  "per_recipe_crafts_per_min": {},
  "per_machine_counts": {},
  "raw_consumption_per_min": {}
}
```

### If infeasible:

```json
{
  "status": "infeasible",
  "max_feasible_target_per_min": number,
  "bottleneck_hint": []
}
```

---

### Belts Input (stdin)

```json
{
  "nodes": [
    { "id": "A", "type": "source|sink|normal", "supply": number }
  ],
  "edges": [
    { "from": "A", "to": "B", "lo": number, "hi": number }
  ],
  "caps": { node: cap }
}
```

---

### Belts Output (stdout)

### If feasible:

```json
{
  "status": "ok",
  "max_flow_per_min": number,
  "flows": [{ "from": "", "to": "", "flow": number }]
}
```

### If infeasible:

```json
{
  "status": "infeasible",
  "cut_reachable": [],
  "deficit": {
    "demand_balance": number,
    "tight_nodes": [],
    "tight_edges": []
  }
}
```

---

## Spec vs Sample (Factory)

Spec says productivity modifies output of recipes.  
Sample interprets target rate **before** productivity.

Your version follows **sample-compatible** interpretation.

---

## Running

### Run samples:

```powershell
cd path\to\repo\part2_assignment\part2_assignment
python run_samples.py
```

### Run factory:

```powershell
python factory/main.py < samples/factory_input.json > out.json
```

### Run belts:

```powershell
python belts/main.py < samples/belts_input.json > out.json
```

### Run tests:

```powershell
cd path\to\repo\part2_assignment\part2_assignment
$env:FACTORY_CMD='python factory/main.py'
$env:BELTS_CMD='python belts/main.py'
pytest -q
```

---

## Files of Interest

- `factory/main.py` — LP-based solver
- `belts/main.py` — max-flow solver
- `run_samples.py` — example runner
- `tests/` — official grading tests
