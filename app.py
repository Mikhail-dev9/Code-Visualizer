"""
Code Visualizer V3.0 — Flask app.
Paste Python code, get a clickable SVG flowchart.
Click any node in the diagram to see its specific details and a live example inline.
"""

import json
from flask import Flask, request, render_template

from parser import parse_and_build_graph
from viz import build_diagram

app = Flask(__name__)


def _handle_viz_error(e):
    """Return a friendly message for known errors."""
    err_name = type(e).__name__
    if err_name == "ExecutableNotFound":
        return "Graphviz is not installed. Install it from https://graphviz.org/download/ and add it to your PATH."
    return f"Something went wrong: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    """Show form on GET. On POST parse code, build SVG diagram, show page with diagram or error."""
    code = ""
    error = None
    svg_diagram = None
    node_details = {}

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if not code:
            error = "Please paste some Python code."
        else:
            try:
                nodes, edges, node_details = parse_and_build_graph(code)
                svg_diagram = build_diagram(nodes, edges)
            except SyntaxError as e:
                error = f"Invalid Python code: {e.msg} (line {e.lineno or '?'})"
            except Exception as e:
                error = _handle_viz_error(e)

    return render_template(
        "index.html",
        code=code,
        error=error,
        svg_diagram=svg_diagram,
        # Pass details as JSON so JavaScript can read them
        node_details_json=json.dumps(node_details),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
