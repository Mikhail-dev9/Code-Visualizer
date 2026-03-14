"""
Parse Python code with ast and build Graphviz diagram data (nodes, edges, details).
V3.0 — Specific explanations using actual variable names + live examples per node.
"""

import ast


def get_label(node):
    """Return a short label for the node to display in the diagram."""
    if isinstance(node, ast.Module):
        return "module"
    if isinstance(node, ast.FunctionDef):
        return f"def {node.name}()"
    if isinstance(node, ast.ClassDef):
        return f"class {node.name}"
    if isinstance(node, ast.For):
        return "for loop"
    if isinstance(node, ast.While):
        return "while loop"
    if isinstance(node, ast.If):
        return "if"
    if isinstance(node, ast.With):
        return "with"
    return type(node).__name__


def _expr_name(node):
    """Return a short readable name for an expression node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_expr_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return f"{_expr_name(node.func)}(...)"
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Subscript):
        return f"{_expr_name(node.value)}[...]"
    return type(node).__name__


def _unparse(node):
    """Safely unparse an AST node to a string."""
    try:
        return ast.unparse(node)
    except Exception:
        return "a condition"


def _get_body_operations(body):
    """Extract a list of plain English descriptions of what happens inside a body."""
    ops = []
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            targets = ", ".join(_expr_name(t) for t in stmt.targets)
            value = _unparse(stmt.value)
            ops.append(f"assigns {value} to {targets}")
        elif isinstance(stmt, ast.AugAssign):
            ops.append(f"updates {_expr_name(stmt.target)} using {_unparse(stmt.value)}")
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            ops.append(f"calls {_expr_name(stmt.value.func)}()")
        elif isinstance(stmt, ast.Return):
            ops.append(f"returns {_unparse(stmt.value) if stmt.value else 'nothing'}")
        elif isinstance(stmt, ast.If):
            ops.append(f"checks condition: {_unparse(stmt.test)}")
        elif isinstance(stmt, ast.For):
            ops.append(f"loops over {_expr_name(stmt.iter)}")
        elif isinstance(stmt, ast.While):
            ops.append(f"repeats while {_unparse(stmt.test)}")
        elif isinstance(stmt, ast.Break):
            ops.append("breaks out of the loop")
        elif isinstance(stmt, ast.Continue):
            ops.append("skips to the next iteration")
        elif isinstance(stmt, ast.Raise):
            ops.append("raises an error")
        elif isinstance(stmt, ast.Delete):
            ops.append(f"deletes {', '.join(_expr_name(t) for t in stmt.targets)}")
    return ops[:5]  # Keep to max 5 operations for readability


def _describe_function(node: ast.FunctionDef):
    """
    Build a specific English description for THIS exact function.
    Uses actual parameter names, return values, and body operations.
    """
    param_names = [arg.arg for arg in node.args.args]
    params_text = ", ".join(param_names) if param_names else "no parameters"

    # Find what the function actually does from its body
    ops = _get_body_operations(node.body)

    # Check for return value
    return_nodes = [n for n in ast.walk(node) if isinstance(n, ast.Return) and n.value]
    has_return = len(return_nodes) > 0
    return_val = _unparse(return_nodes[0].value) if return_nodes else None

    # Build specific summary based on what the function actually does
    if not param_names:
        summary = f"'{node.name}' runs a task using no inputs."
    elif len(param_names) == 1:
        summary = f"'{node.name}' receives '{param_names[0]}' and processes it."
    else:
        summary = f"'{node.name}' receives {params_text} and works with all of them."

    bullets = [f"Inputs: {params_text}."]

    if ops:
        bullets.append("Steps inside: " + "; then ".join(ops) + ".")
    else:
        bullets.append("Steps inside: performs internal operations on the inputs.")

    if has_return and return_val:
        bullets.append(f"Output: returns {return_val}.")
    elif has_return:
        bullets.append("Output: returns a value at the end.")
    else:
        bullets.append("Output: no return value — performs a side effect.")

    # Build a live example
    if param_names:
        example_input = f"{param_names[0]} = 'example_value'"
        if ops:
            example_inside = ops[0]
        else:
            example_inside = "processes the input"
        if return_val:
            example_output = f"returns {return_val}"
        else:
            example_output = "performs action, nothing returned"
    else:
        example_input = "no input needed"
        example_inside = ops[0] if ops else "runs internal operations"
        example_output = "side effect happens (e.g. screen clears, file writes)"

    example = {
        "input": example_input,
        "inside": example_inside,
        "output": example_output,
    }

    return summary, bullets, example


def _describe_loop(node):
    """
    Build a specific English description for THIS exact loop.
    Uses actual variable names and iterable names from the code.
    """
    if isinstance(node, ast.For):
        target = _expr_name(node.target)
        iterable = _expr_name(node.iter)
        ops = _get_body_operations(node.body)

        summary = f"Loops through every item in '{iterable}', storing each one in '{target}'."
        bullets = [
            f"Variable it works with: '{iterable}' (the collection being looped over).",
            f"Each iteration: takes one item from '{iterable}' and calls it '{target}'.",
        ]
        if ops:
            bullets.append("What it does each time: " + "; ".join(ops) + ".")
        else:
            bullets.append(f"What it does each time: runs operations using '{target}'.")
        bullets.append(f"After the loop: '{target}' holds the last item from '{iterable}'.")

        example = {
            "input": f"{iterable} = [item1, item2, item3]",
            "inside": f"takes item1 as {target}, " + (ops[0] if ops else "runs body"),
            "output": f"{target} = item3 (last item), loop ends",
        }

    else:
        # While loop
        cond = _unparse(node.test)
        ops = _get_body_operations(node.body)

        summary = f"Keeps repeating while this condition stays true: {cond}."
        bullets = [
            f"Condition being checked every iteration: {cond}.",
        ]
        if ops:
            bullets.append("Each iteration: " + "; then ".join(ops) + ".")
        else:
            bullets.append("Each iteration: runs the block of code inside.")
        bullets.append("When the condition becomes false the loop stops immediately.")

        example = {
            "input": f"condition: {cond}",
            "inside": ops[0] if ops else "runs loop body",
            "output": "loop exits when condition is False",
        }

    return summary, bullets, example


def _describe_if(node: ast.If):
    """
    Build a specific English description for THIS exact if statement.
    Uses the actual condition and branch operations from the code.
    """
    cond = _unparse(node.test)
    if_ops = _get_body_operations(node.body)
    else_ops = _get_body_operations(node.orelse) if node.orelse else []

    summary = f"Checks if this is true: {cond}. Then takes a different path based on the result."

    bullets = [
        f"Condition tested: {cond}.",
    ]

    if if_ops:
        bullets.append("If TRUE: " + "; ".join(if_ops) + ".")
    else:
        bullets.append("If TRUE: runs the code inside the if block.")

    if else_ops:
        bullets.append("If FALSE: " + "; ".join(else_ops) + ".")
    elif node.orelse:
        bullets.append("If FALSE: runs the else or elif block.")
    else:
        bullets.append("If FALSE: skips this block entirely and moves on.")

    bullets.append(f"Gatekeeper rule: only values that make '{cond}' true will enter the if block.")

    # Build live example from the actual condition
    cond_parts = cond.split(" in ") if " in " in cond else cond.split(" == ") if " == " in cond else [cond]
    if " in " in cond:
        var = cond.split(" in ")[0].strip()
        collection = cond.split(" in ")[1].strip()
        example = {
            "input": f"{var} = 'A'",
            "inside": f"checks if 'A' exists in {collection}",
            "output": "True — enters if block, " + (if_ops[0] if if_ops else "runs body"),
        }
    elif " == " in cond:
        var = cond.split(" == ")[0].strip()
        val = cond.split(" == ")[1].strip()
        example = {
            "input": f"{var} = {val}",
            "inside": f"checks if {var} equals {val}",
            "output": "True — " + (if_ops[0] if if_ops else "enters if block"),
        }
    else:
        example = {
            "input": f"condition: {cond}",
            "inside": "evaluates the condition",
            "output": "True → " + (if_ops[0] if if_ops else "runs if block") + " | False → " + (else_ops[0] if else_ops else "skips block"),
        }

    return summary, bullets, example


def _describe_class(node: ast.ClassDef):
    """
    Build a specific English description for THIS exact class.
    Uses actual method names and what they do.
    """
    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    method_names = [m.name for m in methods]
    methods_text = ", ".join(method_names) if method_names else "no methods"

    # Find __init__ to understand what the class stores
    init = next((m for m in methods if m.name == "__init__"), None)
    if init:
        params = [arg.arg for arg in init.args.args if arg.arg != "self"]
        if params:
            summary = f"'{node.name}' is a blueprint that creates objects storing: {', '.join(params)}."
        else:
            summary = f"'{node.name}' is a blueprint for creating objects."
    else:
        summary = f"'{node.name}' is a blueprint for creating objects with shared behavior."

    bullets = [f"Methods defined: {methods_text}."]

    for m in methods[:3]:  # Describe up to 3 methods
        m_ops = _get_body_operations(m.body)
        m_params = [arg.arg for arg in m.args.args if arg.arg != "self"]
        if m_ops:
            bullets.append(f"  '{m.name}({', '.join(m_params)})': {m_ops[0]}.")
        else:
            bullets.append(f"  '{m.name}': performs operations on the object.")

    # Live example
    if init and (params := [arg.arg for arg in init.args.args if arg.arg != "self"]):
        example_vals = ", ".join(f"'{p}_value'" for p in params)
        example = {
            "input": f"{node.name}({example_vals})",
            "inside": f"__init__ stores {', '.join(params)} as object attributes",
            "output": f"a {node.name} object ready to use with .{method_names[0] if method_names else 'method'}()",
        }
    else:
        example = {
            "input": f"{node.name}()",
            "inside": "creates a new object from the class blueprint",
            "output": f"a {node.name} object with access to: {methods_text}",
        }

    return summary, bullets, example


def collect_nodes(parent_id, parent_node, nodes, edges, details, counter):
    """Walk AST, collect nodes/edges and specific English details per node."""
    for child in ast.iter_child_nodes(parent_node):
        interesting = (ast.FunctionDef, ast.ClassDef, ast.For, ast.While, ast.If, ast.With)
        if not isinstance(child, interesting):
            continue
        counter[0] += 1
        nid = f"n{counter[0]}"
        label = get_label(child)
        nodes.append((nid, label))
        edges.append((parent_id, nid))

        if isinstance(child, ast.FunctionDef):
            summary, bullets, example = _describe_function(child)
        elif isinstance(child, ast.ClassDef):
            summary, bullets, example = _describe_class(child)
        elif isinstance(child, (ast.For, ast.While)):
            summary, bullets, example = _describe_loop(child)
        elif isinstance(child, ast.If):
            summary, bullets, example = _describe_if(child)
        else:
            summary = f"This '{label}' block manages a group of operations."
            bullets = ["It handles a set of related statements together."]
            example = {
                "input": "enters the block",
                "inside": "executes statements inside",
                "output": "block finishes, execution continues",
            }

        details[nid] = {
            "label": label,
            "summary": summary,
            "bullets": bullets,
            "example": example,
        }

        collect_nodes(nid, child, nodes, edges, details, counter)


def parse_and_build_graph(code):
    """
    Parse code with ast, return (nodes, edges, details) for diagram.
    nodes: list of (id, label).
    edges: list of (from_id, to_id).
    details: dict[node_id] = {label, summary, bullets, example}.
    Raises SyntaxError if code is invalid.
    """
    tree = ast.parse(code)
    nodes = [("n0", "module")]
    edges = []
    details = {
        "n0": {
            "label": "module",
            "summary": "The top-level module that contains all the code you pasted.",
            "bullets": [
                "It holds all imports, global variables, functions, and classes.",
                "Every other node in this diagram lives inside this module.",
            ],
            "example": {
                "input": "you paste your Python code",
                "inside": "the module loads all top-level definitions",
                "output": "all functions, classes, and statements are ready to run",
            },
        }
    }
    counter = [0]
    collect_nodes("n0", tree, nodes, edges, details, counter)
    return nodes, edges, details
