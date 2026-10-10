"""Check the repository rules: line length, function size, complexity."""

import ast
import sys
from pathlib import Path

MAX_LINE = 80
MAX_FILE_LINES = 1000
MAX_FUNC_LINES = 40
MAX_ARGS = 7
MAX_COMPLEXITY = 10
ALLOWED_NUMBERS = (0, 1, -1)
BRANCH_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With,
    ast.IfExp, ast.comprehension, ast.Assert,
)


def complexity(func):
    """Return the cyclomatic complexity of a function."""
    total = 1
    for node in ast.walk(func):
        if isinstance(node, BRANCH_NODES):
            total += 1
        elif isinstance(node, ast.BoolOp):
            total += len(node.values) - 1
    return total


def magic_numbers(tree):
    """Yield line numbers of numeric literals used in comparisons."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for part in [node.left, *node.comparators]:
            if isinstance(part, ast.Constant) and not isinstance(
                    part.value, (str, bytes, bool, type(None))):
                if part.value not in ALLOWED_NUMBERS:
                    yield part.lineno


def check_function(path, func):
    """Return problems found in one function."""
    problems = []
    size = func.end_lineno - func.lineno + 1
    args = func.args
    count = len(args.args) + len(args.kwonlyargs)
    if size > MAX_FUNC_LINES:
        problems.append(f"{path}:{func.lineno}: long function {func.name}")
    if count > MAX_ARGS:
        problems.append(f"{path}:{func.lineno}: many args {func.name}")
    if complexity(func) > MAX_COMPLEXITY:
        problems.append(f"{path}:{func.lineno}: complex {func.name}")
    if ast.get_docstring(func) is None:
        problems.append(f"{path}:{func.lineno}: no docstring {func.name}")
    return problems


def check_file(path):
    """Return problems found in one Python file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    problems = []
    if len(lines) > MAX_FILE_LINES:
        problems.append(f"{path}: file is too big")
    for number, line in enumerate(lines, 1):
        if len(line) > MAX_LINE:
            problems.append(f"{path}:{number}: line is too long")
        if line.lstrip().startswith("#"):
            problems.append(f"{path}:{number}: comment instead of docstring")
    tree = ast.parse(text)
    for number in magic_numbers(tree):
        problems.append(f"{path}:{number}: magic number in comparison")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            problems.extend(check_function(path, node))
    return problems


def main():
    """Check all Python files of the repository."""
    root = Path(__file__).resolve().parent.parent
    problems = []
    for path in sorted(root.rglob("*.py")):
        if ".git" not in path.parts:
            problems.extend(check_file(path.relative_to(root)))
    print("\n".join(problems) if problems else "style: ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
