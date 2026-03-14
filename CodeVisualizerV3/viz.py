"""
Build a Graphviz diagram from nodes and edges.
V3.0 — Returns SVG string instead of PNG bytes so nodes are individually clickable.
"""

import graphviz


def build_diagram(nodes, edges):
    """
    Create a flowchart from (nodes, edges).
    nodes: [(id, label), ...]
    edges: [(from_id, to_id), ...]
    Returns SVG string (not PNG bytes) so nodes can be clicked in the browser.
    """
    dot = graphviz.Digraph(comment="Code structure")
    dot.attr(rankdir="TB", fontname="Segoe UI", nodesep="0.5", ranksep="0.6")

    for nid, label in nodes:
        # Each node gets its id as an SVG id so JavaScript can find and click it
        dot.node(
            nid,
            label,
            fontname="Segoe UI",
            shape="box",
            margin="0.25,0.15",
            style="filled",
            fillcolor="#1e2533",
            fontcolor="#e6edf3",
            color="#238636",
            id=nid,          # This becomes the SVG element id
            tooltip=label,   # Shows label on hover
        )

    for a, b in edges:
        dot.edge(a, b, color="#58a6ff")

    # Return SVG as a string so we can embed it directly in HTML
    svg_bytes = dot.pipe(format="svg")
    return svg_bytes.decode("utf-8")
