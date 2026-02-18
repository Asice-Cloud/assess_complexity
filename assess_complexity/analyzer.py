from clang import cindex
from collections import defaultdict


LOOP_KINDS = {
    cindex.CursorKind.FOR_STMT,
    cindex.CursorKind.WHILE_STMT,
    cindex.CursorKind.DO_STMT,
}


def _max_loop_depth(node):
    max_child = 0
    for c in node.get_children():
        depth = _max_loop_depth(c)
        if depth > max_child:
            max_child = depth

    add = 1 if node.kind in LOOP_KINDS else 0
    return add + max_child


def _count_calls(node, func_name):
    """Return list of call cursors inside node (recursively)."""
    calls = []
    for c in node.get_children():
        if c.kind == cindex.CursorKind.CALL_EXPR:
            calls.append(c)
        calls.extend(_count_calls(c, func_name))
    return calls


def _call_targets(call_cursor):
    """Try to resolve direct callee spelling for a CALL_EXPR cursor."""
    try:
        callee = next(call_cursor.get_children())
        return callee.spelling
    except StopIteration:
        return None


def _ancestor_loop_depth(node, stop_node):
    """Count loop-like ancestors between node and stop_node (exclusive)."""
    depth = 0
    cur = node.semantic_parent
    while cur is not None and cur != stop_node:
        if cur.kind in LOOP_KINDS:
            depth += 1
        cur = cur.semantic_parent
    return depth


def _initial_complexity(loop_depth, self_calls):
    # Structured complexity: {'type': 'poly', 'exp': k} or {'type':'exp'} or {'type':'const'}
    if self_calls > 1:
        return {"type": "exp"}
    if self_calls == 1:
        return {"type": "poly", "exp": 1}
    if loop_depth == 0:
        return {"type": "const", "exp": 0}
    return {"type": "poly", "exp": loop_depth}


def _format_complexity(struct):
    if struct["type"] == "exp":
        return "O(2^n) (heuristic exponential recursion)"
    if struct["type"] == "const":
        return "O(1)"
    if struct["type"] == "poly":
        e = struct.get("exp", 0)
        if e == 0:
            return "O(1)"
        if e == 1:
            return "O(n)"
        return f"O(n^{e})"
    return "O(?)"


def analyze_file(path, clang_args=None):
    """Analyze C/C++ file and return heuristic complexity per function.

    Returns a dict: { function_name: {complexity, loop_nesting, calls, self_calls, callees}}.
    Uses a simple interprocedural propagation: callee polynomial exponents add when called inside loops.
    """
    if clang_args is None:
        clang_args = ["-std=c11"]

    index = cindex.Index.create()
    tu = index.parse(path, args=clang_args)

    funcs = {}
    # collect functions
    for node in tu.cursor.get_children():
        if node.kind == cindex.CursorKind.FUNCTION_DECL and node.is_definition():
            funcs[node.spelling] = node

    info = {}
    # basic metrics and call sites
    for name, node in funcs.items():
        loop_depth = _max_loop_depth(node)
        calls = _count_calls(node, name)
        call_infos = []
        self_calls = 0
        for call in calls:
            target = _call_targets(call)
            call_loop = _ancestor_loop_depth(call, node)
            call_infos.append((target, call_loop))
            if target == name:
                self_calls += 1

        info[name] = {
            "node": node,
            "loop_nesting": loop_depth,
            "call_sites": call_infos,
            "calls": len(call_infos),
            "self_calls": self_calls,
            "complex_struct": _initial_complexity(loop_depth, self_calls),
        }

    # propagate complexities through call graph (fixed-point iterations)
    changed = True
    iterations = 0
    while changed and iterations < 10:
        iterations += 1
        changed = False
        for name, data in info.items():
            cur = data["complex_struct"]
            if cur["type"] == "exp":
                continue
            exp = 0 if cur["type"] == "const" else cur.get("exp", 0)
            # consider each call site
            for target, call_loop in data["call_sites"]:
                if target is None or target not in info:
                    continue
                callee_struct = info[target]["complex_struct"]
                if callee_struct["type"] == "exp":
                    # caller becomes exponential if calls exponential callee inside any context
                    new_struct = {"type": "exp"}
                    if new_struct != cur:
                        data["complex_struct"] = new_struct
                        changed = True
                        cur = new_struct
                        break
                elif callee_struct["type"] == "poly":
                    # if callee has exponent e and call is inside additional loop depth d,
                    # total exponent candidate = call_loop + callee_exp
                    candidate = call_loop + callee_struct.get("exp", 0)
                    if candidate > exp:
                        exp = candidate
            else:
                # only update if not set to exponential
                new_struct = {"type": "poly", "exp": exp} if exp > 0 else {"type": "const", "exp": 0}
                if new_struct != cur:
                    data["complex_struct"] = new_struct
                    changed = True
                    cur = new_struct

    # prepare results
    results = {}
    for name, data in info.items():
        struct = data["complex_struct"]
        results[name] = {
            "complexity": _format_complexity(struct),
            "loop_nesting": data["loop_nesting"],
            "calls": data["calls"],
            "self_calls": data["self_calls"],
            "callees": [c for c, _d in data["call_sites"] if c is not None],
        }
    return results
