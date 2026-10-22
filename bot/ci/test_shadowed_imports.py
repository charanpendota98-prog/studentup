#!/usr/bin/env python3
"""Catch `UnboundLocalError` from a function-local import that shadows a
module-level one.

Run:  python ci/test_shadowed_imports.py     (no pytest needed)

The real bug this guards: `main.py` imported `notifier` at module level, then
had `from . import notifier` *later inside* `run()`.  That single line made
`notifier` function-local, so the earlier
`notifier.send_opportunity_digest()` raised UnboundLocalError on every
scheduled run — and because the call sits in a `_soft_fail()` try/except, the
opportunity digest just silently never ran.

A local import is fine as long as the name is not used before it.  So this
reports only *use-before-local-import*.
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def module_level_names(tree: ast.Module) -> set:
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names |= {(a.asname or a.name.split(".")[0]) for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            names |= {(a.asname or a.name) for a in node.names}
    return names


def scan(path: pathlib.Path) -> list:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    top = module_level_names(tree)
    problems = []
    for fn in (n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
        # name -> first line where this function imports it locally
        bound = {}
        for node in ast.walk(fn):
            if isinstance(node, ast.Import):
                for a in node.names:
                    bound.setdefault(a.asname or a.name.split(".")[0], node.lineno)
            elif isinstance(node, ast.ImportFrom):
                for a in node.names:
                    bound.setdefault(a.asname or a.name, node.lineno)
        shadowed = {n: ln for n, ln in bound.items() if n in top}
        if not shadowed:
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load):
                continue
            line = shadowed.get(node.id)
            if line is not None and node.lineno < line:
                problems.append("%s:%d %s() uses '%s' before its local import at line %d"
                                % (path.name, node.lineno, fn.name, node.id, line))
    return problems


def main() -> int:
    files = sorted((ROOT / "autoblog").glob("*.py"))
    if not files:
        print("FAIL: no autoblog/*.py found")
        return 1
    problems = []
    for path in files:
        problems += scan(path)
    print("  scanned %d modules" % len(files))
    if problems:
        for p in problems:
            print("  FAIL %s" % p)
        print("UnboundLocalError waiting to happen — remove the local import "
              "(the module-level one already covers it).")
        return 1
    print("  no use-before-local-import shadows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
