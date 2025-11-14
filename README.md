# ERP.AI Engineering Assessment - Part 2

## README.md

This document outlines the design and implementation choices for the Factory Steady State and Bounded Belts problems.

### Factory Modeling Choices

#### Item Balances and Conservation Equations

The Factory Steady State problem can be modeled as a Linear Program (LP). We introduce a variable \(x_r\) for each recipe \(r\), representing its crafts per minute. 

For each item \(i\), the conservation equation is formulated as:

\\[ \\sum_r [\\text{out}_r[i] \\cdot (1 + \\text{prod}_m) \\cdot x_r] - \\sum_r [\\text{in}_r[i] \\cdot x_r] = b[i] \\]

Where:
*   **Target item \(t\)**: \(b[t] = \\text{target\\_rate}\) (exact match).
*   **Intermediates**: \(b[i] = 0\) (perfect balance).
*   **Raw items with supply caps**: \(b[i] \\le 0\) (net consumption) and \(|b[i]| \\le \\text{raw\\_cap}[i]\). This is handled by introducing slack variables for raw consumption and ensuring they are within limits.

#### Raw Consumption and Machine Capacity Constraints

**Raw Consumption:** For each raw item \(j\), the total consumption must not exceed its supply cap. We define consumption as:

\\[ \\sum_r [\\text{in}_r[j] \\cdot x_r] \\le \\text{raw\\_cap}[j] \\]

**Machine Capacity:** For each machine type \(m\), the total machines used by recipes running on that machine type must not exceed its maximum capacity.

First, the effective crafts per minute for a recipe \(r\) on machine \(m\) is calculated as:

\\[ \\text{eff\\_crafts\\_per\\_min}(r) = \\text{machines}[m].\\text{crafts\\_per\\_min} \\cdot (1 + \\text{speed}) \\cdot \\frac{60}{\\text{time\\_s}(r)} \\]

Then, the machines used by recipe \(r\) are \( \\text{machines\\_used\\_by\\_r} = \\frac{x_r}{\\text{eff\\_crafts\\_per\\_min}(r)} \). The constraint for machine type \(m\) is:

\\[ \\sum_{r \\text{ uses } m} \\text{machines\\_used\\_by\\_r} \\le \\text{max\\_machines}[m] \\]

#### Module Application

Modules (speed and productivity) are applied per machine type. All recipes running on the same machine type inherit the same speed and productivity modifiers. Speed multiplies the base machine speed, and productivity multiplies only the outputs of a recipe.

#### Handling of Cycles, Byproducts, and Self-Contained Recipes

Cycles and byproducts are naturally handled by the conservation equations where \(b[i] = 0\) for intermediates. The LP solver will find a steady state where all intermediate items are balanced. If a recipe produces a byproduct not consumed elsewhere, its \(b[i]\) will be 0, implying a balance or accumulation if the system can sustain it.

#### Tie-breaking in Machine Count

The problem states that if multiple solutions exist, choose one that uses the fewest total machines. This is a secondary objective. A two-phase approach or a single linear program with weighted objectives can be used. For a single LP, the objective function would be to minimize the total sum of machines used:

\\[ \\text{minimize: } \\sum_m \\sum_{r \\text{ uses } m} \\frac{x_r}{\\text{eff\\_crafts\\_per\\_min}(r)} \\]

#### Infeasibility Detection and Reporting

If no feasible solution exists at the target rate, the problem requires returning the maximum feasible target rate and bottleneck hints. This can be achieved through a binary search on the target rate, where each step involves solving an LP. The bottleneck hints can be derived from the dual variables or sensitivity analysis of the LP at the maximum feasible rate.

### Belts Modeling Choices

#### Max-Flow with Lower Bounds

The Bounded Belts problem can be solved using a maximum flow algorithm with modifications for lower bounds and node capacities. The general approach involves transformations to convert the problem into a standard max-flow problem.

**Transformation Steps and Order of Operations:**

1.  **Node Splitting for Capacity Constraints:** For each capped node \(v\) (not a source or sink), it's split into two nodes: \(v_{in}\) and \(v_{out}\). An edge \(v_{in} \\to v_{out}\) is added with capacity equal to the node's cap. All incoming edges to \(v\) are redirected to \(v_{in}\), and all outgoing edges from \(v\) are redirected from \(v_{out}\).

2.  **Lower Bounds via Transformation:** For each edge \((u \\to v)\) with lower bound \(lo\) and upper bound \(hi\):
    *   Reduce the edge capacity to \(hi - lo\).
    *   Adjust node demands/supplies: add \(lo\) as demand at \(v\) and subtract \(lo\) (add as supply) at \(u\).
    *   After solving the max-flow, add \(lo\) back to the computed flow to recover the original flow values.

#### Feasibility Check Strategy

After applying the lower bound transformation, a feasibility check is performed. A super-source \(s^*\) and a super-sink \(t^*\) are introduced. Edges are added from \(s^*\) to nodes with positive imbalance (demand) and from nodes with negative imbalance (supply) to \(t^*\). A max-flow from \(s^*\) to \(t^*\) is run. If the max-flow equals the total demand from \(s^*\), the lower bounds are feasible.

#### How Infeasibility Certificates (Min-Cut) Are Computed and Reported

If the max-flow for the feasibility check does not saturate all edges from the super-source, the system is infeasible. The min-cut in the residual graph provides the certificate. The nodes reachable from \(s^*\) in the residual graph define the `cut_reachable`. The `deficit` can be calculated from the unsatisfied flow, and `tight_nodes` and `tight_edges` are identified from the cut.

### Numeric Approach

**Tolerances:** Numeric tolerances for floating-point comparisons will be set to \(1 \\cdot 10^{-9}\) (e.g., `abs(a - b) < 1e-9`).

**Solver:** For the Factory problem, a linear programming solver (e.g., `PuLP` or `scipy.optimize.linprog`) will be used. For the Belts problem, a max-flow algorithm (e.g., Edmonds-Karp or Dinic) will be implemented.

**Tie-breaking:** For determinism, if multiple solutions yield the same minimum total machines (Factory) or max-flow (Belts), tie-breaking will be done by lexicographical order of recipe names or edge identifiers, respectively, when iterating or selecting paths.

### Failure Modes & Edge Cases

#### Factory

*   **Cycles in recipes:** Handled naturally by the conservation equations in the LP. The solver will find a balanced state.
*   **Infeasible raw supplies or machine counts:** The LP will report infeasibility. The system will then perform a binary search for the maximum feasible target rate and identify bottlenecks.
*   **Degenerate or redundant recipes:** The LP solver should handle these gracefully, potentially leading to multiple optimal solutions, in which case the tie-breaking rule applies.

#### Belts

*   **Disconnected graph components:** The max-flow algorithm will correctly identify that flow cannot reach the sink if components are disconnected from sources.
*   **Zero or negative capacities/bounds:** The problem statement implies non-negative flows and capacities. Edge cases with zero bounds will be handled by the transformations.

## Input / Output — exact formats

These CLIs communicate via JSON on stdin/stdout. Below are the exact fields expected and produced.

Factory input (JSON on stdin) — required fields:
- `machines`: map machine_name -> { `crafts_per_min`: number }
- `recipes`: map recipe_name -> { `machine`: machine_name, `time_s`: number, `in`: {item: qty}, `out`: {item: qty} }
- `modules` (optional): map machine_name -> { `prod`: number, `speed`: number }
- `limits`: { `raw_supply_per_min`: {item: cap, ...}, `max_machines`: {machine: cap, ...} }
- `target`: { `item`: item_name, `rate_per_min`: number }

Factory output (JSON on stdout):
- If feasible:
    - `status`: `"ok"`
    - `per_recipe_crafts_per_min`: map recipe_name -> crafts_per_min (numbers)
    - `per_machine_counts`: map machine_name -> machine_count (numbers)
    - `raw_consumption_per_min`: map raw_item -> consumption_per_min (numbers)
- If infeasible:
    - `status`: `"infeasible"`
    - `max_feasible_target_per_min`: number
    - `bottleneck_hint`: [string, ...]

Belts input (JSON on stdin) — required fields:
- `nodes`: list of nodes, each node: `{ "id": str, "type": "source"|"sink"|"normal", "supply": number (source only) }`
- `edges`: list of edges, each `{ "from": id, "to": id, "lo": number, "hi": number }`
- `caps` (optional): map node_id -> capacity (applies to non-source/sink nodes)

Belts output (JSON on stdout):
- If feasible:
    - `status`: `"ok"`
    - `max_flow_per_min`: number
    - `flows`: list of `{ "from": id, "to": id, "flow": number }`
- If infeasible:
    - `status`: `"infeasible"`
    - `cut_reachable`: list of node ids on the source side of the min-cut
    - `deficit`: object with `demand_balance`, `tight_nodes`, `tight_edges`

## Why there are two factory JSON variants (spec vs sample)

During implementation and testing we discovered a small but important ambiguity between the written problem description and the sample input/output that was provided with the assignment. The ambiguity is about how machine productivity (`modules[].prod`) should affect the reported target production rate:

- Interpretation A — "spec-strict": productivity multiplies recipe outputs. If a recipe's output is increased by productivity, the solver must account for that when computing how many machines are needed and how raw inputs flow through the network. This is the most literal reading of the spec where `prod` increases the per-craft output.
- Interpretation B — "sample-compatible": the provided sample appears to treat the `target.rate_per_min` as the requested crafts-per-minute that must be produced (i.e. the target is not adjusted by productivity). In other words, the solver must plan machines and upstream recipes so that the final produced item equals the target rate reported in the input JSON.

Because the sample tests included with the assignment follow Interpretation B while the textual spec suggests Interpretation A, we intentionally generate and preserve two JSON variants during development:

- `factory_input_spec.json` (conceptually): models inputs for the spec-strict interpretation (productivity applied to outputs). Use this if you prefer strict adherence to the textual spec.
- `factory_input_sample.json` (conceptually): a sample-compatible input variant where the test harness expects the `target.rate_per_min` to be realized exactly as the final crafts/min.

Which one to use:
- The included automated tests (and the adjoint sample outputs) are aligned with the sample-compatible interpretation. If your goal is to pass the provided tests as-is, use the sample-compatible JSON.
- If you prefer to follow the textual spec strictly (prod applied to outputs), use the spec-strict JSON and be aware the sample tests will not match exactly; you would need to update the test expectations.

This repository includes small generators (`gen_factory.py`) and a convenient runner (`run_samples.py`). The generator produces a canonical sample JSON for quick manual runs; if you want I can add an explicit `factory_input_spec.json` file as well and add a command-line flag to `run_samples.py` to pick which variant to run.

---

If you'd like, I can now:

1. Add an explicit `factory_input_spec.json` file and modify `run_samples.py` to support a `--spec` flag. OR
2. Keep the repository as-is (tests expect sample-compatible behavior) and update documentation/tests to call out the chosen behavior clearly.

Tell me which option you prefer and I'll implement it and re-run the tests.
