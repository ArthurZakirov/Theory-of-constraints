import plotly.graph_objects as go
from collections import defaultdict, deque

def plot_sankey_with_visual_reservoirs(edges, capacities, reservoirs=None, show_legend=True):
    if reservoirs is None:
        reservoirs = {}

    graph = defaultdict(list)
    in_deg = defaultdict(int)
    all_nodes = set()
    for u, v in edges:
        graph[u].append(v)
        in_deg[v] += 1
        all_nodes.update([u, v])

    topo_order = []
    q = deque([n for n in all_nodes if in_deg[n] == 0])
    while q:
        node = q.popleft()
        topo_order.append(node)
        for nei in graph[node]:
            in_deg[nei] -= 1
            if in_deg[nei] == 0:
                q.append(nei)

    node_flow = {n: float('inf') for n in all_nodes}
    for n in topo_order:
        if all(m not in graph or len(graph[m]) == 0 for m in all_nodes if m != n):
            node_flow[n] = float('inf')

    edge_flows = {}
    for u in topo_order:
        for v in graph[u]:
            cap = capacities[(u, v)]
            available = min(node_flow[u], cap)
            edge_flows[(u, v)] = available
            node_flow[v] = min(node_flow[v], available)

    inflow_by_node = defaultdict(float)
    outflow_by_node = defaultdict(float)

    for (u, v), val in edge_flows.items():
        inflow_by_node[v] += val
        outflow_by_node[u] += val

    label_list = sorted(all_nodes)
    node_indices = {n: i for i, n in enumerate(label_list)}

    # Add synthetic reservoir nodes
    for node, config in reservoirs.items():
        if config.get("show", False):
            r_name = f"Reservoir: {node}"
            label_list.append(r_name)
            node_indices[r_name] = len(label_list) - 1

    sources, targets, values, colors = [], [], [], []

    # Real flows
    for (u, v) in edges:
        used = edge_flows[(u, v)]
        cap = capacities[(u, v)]

        sources.append(node_indices[u])
        targets.append(node_indices[v])
        values.append(used)
        colors.append("rgba(0,200,0,0.6)")

        if cap > used:
            sources.append(node_indices[u])
            targets.append(node_indices[v])
            values.append(cap - used)
            colors.append("rgba(220,0,0,0.3)")

    # Visual reservoirs as gray inflow nodes
    for node, cfg in reservoirs.items():
        if not cfg.get("show", False):
            continue
        r_node = f"Reservoir: {node}"
        init = cfg.get("initial", 0)
        delta = inflow_by_node[node] - outflow_by_node[node]
        level = init + delta

        sources.append(node_indices[r_node])
        targets.append(node_indices[node])
        values.append(level)
        colors.append("rgba(180,180,180,0.4)")  # gray

    # Custom label formatting (optional)
    final_labels = label_list

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=final_labels,
            color=["#cce5cc" if not label.startswith("Reservoir:") else "#dddddd" for label in final_labels]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])

    if show_legend:
        fig.add_annotation(
            x=1.05, y=1.00,
            xref='paper', yref='paper',
            showarrow=False,
            align='left',
            text="<b>Legend</b><br>"
                 "<span style='color:green'>Green</span>: Utilized capacity<br>"
                 "<span style='color:red'>Red</span>: Wasted capacity<br>"
                 "<span style='color:gray'>Gray</span>: Reservoir inflow<br>"
                 "Reservoirs show inflow - outflow + initial",
            bordercolor="black",
            borderwidth=1,
            bgcolor="white",
            font=dict(size=12)
        )

    fig.update_layout(
        title_text="Dynamic Sankey with Visual Reservoir Nodes",
        font_size=12,
        margin=dict(r=250)
    )

    fig.write_html("pipeline.html")
    print("✔️ Saved to sankey_visual_reservoirs.html")

# -------------------------------
# ▶️ Example Usage
# -------------------------------
edges = [
    ("A", "B"), ("A", "C"),
    ("B", "D"), ("C", "D"),
    ("D", "E1"), ("D", "E2")
]

capacities = {
    ("A", "B"): 100,
    ("A", "C"): 150,
    ("B", "D"): 80,
    ("C", "D"): 70,
    ("D", "E1"): 90,
    ("D", "E2"): 60
}

reservoirs = {
    "A": {"initial": 50, "show": True},
    "C": {"initial": 30, "show": True},
    "D": {"initial": 20, "show": True}  # not shown
}

plot_sankey_with_visual_reservoirs(edges, capacities, reservoirs)
