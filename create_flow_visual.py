import plotly.graph_objects as go
from collections import defaultdict, deque

def plot_dynamic_bottleneck_sankey(edges, capacities):
    # Step 1: Build graph and reverse graph
    graph = defaultdict(list)
    in_deg = defaultdict(int)
    all_nodes = set()

    for u, v in edges:
        graph[u].append(v)
        in_deg[v] += 1
        all_nodes.update([u, v])

    # Step 2: Topological sort
    topo_order = []
    q = deque([n for n in all_nodes if in_deg[n] == 0])
    while q:
        node = q.popleft()
        topo_order.append(node)
        for nei in graph[node]:
            in_deg[nei] -= 1
            if in_deg[nei] == 0:
                q.append(nei)

    # Step 3: Initialize flow to each node (min bottleneck so far)
    node_flow = {n: float('inf') for n in all_nodes}
    for n in topo_order:
        if all(in_deg[m] == 0 for m in all_nodes if m != n):  # source node
            node_flow[n] = float('inf')  # infinite source

    # Step 4: Propagate flow forward
    edge_flows = {}
    for u in topo_order:
        for v in graph[u]:
            cap = capacities[(u, v)]
            available = min(node_flow[u], cap)
            edge_flows[(u, v)] = available
            node_flow[v] = min(node_flow[v], available)

    # Step 5: Assign indices to nodes
    label_list = sorted(all_nodes)
    node_indices = {n: i for i, n in enumerate(label_list)}

    sources, targets, values, colors = [], [], [], []

    for (u, v) in edges:
        used = edge_flows[(u, v)]
        cap = capacities[(u, v)]

        # Green: actual flow
        sources.append(node_indices[u])
        targets.append(node_indices[v])
        values.append(used)
        colors.append("rgba(0, 200, 0, 0.6)")

        # Red: unused capacity
        if cap > used:
            sources.append(node_indices[u])
            targets.append(node_indices[v])
            values.append(cap - used)
            colors.append("rgba(220, 0, 0, 0.3)")

    # Step 6: Plot Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=label_list,
            color=["#cce5cc"] * len(label_list)
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])

    fig.update_layout(
        title_text="Dynamic DAG Bottleneck Flow Visualization",
        font_size=12
    )
    fig.write_html("pipeline.html")
    print("Saved to dag_bottleneck_sankey.html")

# -----------------------------------
# ▶️ Example Usage
# -----------------------------------
edges = [
    ("A", "B"), ("A", "C"),
    ("C", "D"),
    ("D", "E1"), ("D", "E2")
]

capacities = {
    ("A", "B"): 100,
    ("A", "C"): 150,
    ("B", "D"): 30,
    ("C", "D"): 30,
    ("D", "E1"): 60,
    ("D", "E2"): 60
}

plot_dynamic_bottleneck_sankey(edges, capacities)
