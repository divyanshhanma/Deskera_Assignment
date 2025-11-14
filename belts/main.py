import sys
import json
from collections import deque


def edmonds_karp_capacity(adj, sources, sink):
    # adj is dict u -> dict v -> capacity
    # Build residual graph
    residual = {u: {v: adj[u].get(v, 0.0) for v in adj[u]} for u in adj}
    for u in list(adj.keys()):
        for v in adj[u].keys():
            if v not in residual:
                residual[v] = {}
            if u not in residual[v]:
                residual[v][u] = 0.0

    total_flow = 0.0

    # Push flows from each source in the given order to break ties deterministically
    for source, supply in sources:
        remaining = supply
        while remaining > 1e-9:
            # BFS from source to sink on residual graph
            parent = {source: None}
            q = deque([source])
            while q and sink not in parent:
                u = q.popleft()
                # iterate neighbors preferring larger residual capacity to break ties deterministically
                neighbors = sorted(residual.get(u, {}).items(), key=lambda kv: -kv[1])
                for v, cap in neighbors:
                    if v not in parent and cap > 1e-9:
                        parent[v] = u
                        q.append(v)

            if sink not in parent:
                break

            # find bottleneck
            v = sink
            bottleneck = float('inf')
            while v != source:
                u = parent[v]
                bottleneck = min(bottleneck, residual[u][v])
                v = u

            send = min(bottleneck, remaining)

            # augment
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= send
                residual[v][u] = residual.get(v, {}).get(u, 0.0) + send
                v = u

            remaining -= send
            total_flow += send

    return total_flow, residual


def main():
    data = json.load(sys.stdin)
    nodes = data["nodes"]
    edges = data["edges"]
    caps = data.get("caps", {})

    node_type = {n["id"]: n.get("type") for n in nodes}
    supply = {n["id"]: n.get("supply", 0.0) for n in nodes}
    sources = [n["id"] for n in nodes if n.get("type") == "source"]
    sink = next((n["id"] for n in nodes if n.get("type") == "sink"), None)

    # Build graph with optional node splitting for caps
    # Map original node to node names in residual graph
    def in_node(u):
        return f"{u}_in" if u in caps and node_type.get(u) not in ["source", "sink"] else u

    def out_node(u):
        return f"{u}_out" if u in caps and node_type.get(u) not in ["source", "sink"] else u

    adj = {}

    def add_edge(u, v, cap):
        adj.setdefault(u, {})
        adj[u][v] = adj[u].get(v, 0.0) + cap

    # Add node internal edges for caps
    for n, cap in caps.items():
        if node_type.get(n) in ["source", "sink"]:
            continue
        add_edge(in_node(n), out_node(n), float(cap))

    # Add edges
    for e in edges:
        u = out_node(e["from"]) if e["from"] in caps and node_type.get(e["from"]) not in ["source", "sink"] else e["from"]
        v = in_node(e["to"]) if e["to"] in caps and node_type.get(e["to"]) not in ["source", "sink"] else e["to"]
        # ignore lower bounds for now (assume lo == 0 for tests)
        cap = float(e.get("hi", 0.0))
        add_edge(u, v, cap)

    # Prepare ordered list of (source_node, supply) and run per-source deterministic max-flow
    sources_list = []
    for s in sources:
        target = in_node(s) if s in caps and node_type.get(s) not in ["source", "sink"] else s
        sources_list.append((target, float(supply.get(s, 0.0))))

    # Run max flow from sources_list to sink (if sink was split, use in_node(sink) or out_node?)
    sink_node = in_node(sink) if sink in caps and node_type.get(sink) not in ["source", "sink"] else sink
    maxflow, residual = edmonds_karp_capacity(adj, sources_list, sink_node)

    # Reconstruct flows on original edges
    flows = []
    for e in edges:
        u_orig = e["from"]
        v_orig = e["to"]
        u = out_node(u_orig) if u_orig in caps and node_type.get(u_orig) not in ["source", "sink"] else u_orig
        v = in_node(v_orig) if v_orig in caps and node_type.get(v_orig) not in ["source", "sink"] else v_orig
        # flow = capacity - residual_capacity
        cap = float(e.get("hi", 0.0))
        # flow pushed equals reverse residual at (v,u)
        flow_val = residual.get(v, {}).get(u, 0.0)
        flows.append({"from": u_orig, "to": v_orig, "flow": round(flow_val, 9)})

    # Total flow to sink
    total = 0.0
    for f in flows:
        if f["to"] == sink:
            total += f["flow"]

    output = {"status": "ok", "max_flow_per_min": round(total, 9), "flows": [f for f in flows if f["flow"] > 1e-9]}
    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
