from select.helper.whereChecksHelper import validateBooleanExpr
from select.helper.groupByChecksHelper import normalize, containsAggregate
from select.helper.utils import isColumnToken


def extractHaving(tokens):
    """
    Extracts HAVING clause tokens.
    Stops at OUTER ORDER BY or LIMIT.
    """
    depth = 0
    start = None

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # 🔥 outer HAVING only
        if depth == 0 and tok == "having":
            start = i + 1
            break

    if start is None:
        return None

    end = len(tokens)
    depth = 0

    for i in range(start, len(tokens)):
        tok = tokens[i]

        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # 🔥 stop only at OUTER clauses
        if depth == 0 and tok in {"order", "limit"}:
            end = i
            break

    return tokens[start:end]


def splitHavingExprs(tokens):
    """
    Splits HAVING expressions on top-level AND / OR.
    Parenthesized expressions are preserved.
    """
    exprs = []
    depth = 0
    start = 0

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and tok in {"and", "or"}:
            exprs.append(tokens[start:i])
            start = i + 1

    exprs.append(tokens[start:])
    return exprs


# Comparison operators allowed in HAVING
COMPARISON_OPS = {"=", "!=", "<", ">", "<=", ">="}


def splitComparison(expr):
    """
    Splits an expression into (lhs, operator, rhs).
    Only splits on top-level comparison operators.
    """
    expr = stripParens(expr)
    depth = 0

    for i, tok in enumerate(expr):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and tok in COMPARISON_OPS:
            return expr[:i], tok, expr[i + 1:]

    return None, None, None


def stripParens(expr):
    """
    Removes redundant outer parentheses from an expression.
    """
    expr = expr[:]

    while len(expr) >= 3 and expr[0] == "(" and expr[-1] == ")":
        depth = 0
        valid = True

        for i, tok in enumerate(expr):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1

            # If outer parens close early, they are not redundant
            if depth == 0 and i < len(expr) - 1:
                valid = False
                break

        if not valid:
            break

        expr = expr[1:-1]

    return expr


def isValidHavingLHS(expr, group_set, alias_set):
    """
    Validates the left-hand side of a HAVING comparison.

    Allowed:
    - aggregate expressions
    - grouped columns
    - SELECT aliases
    """
    expr = stripParens(expr)

    # Aggregate expression → always valid
    if containsAggregate(expr):
        return True

    # Single column or alias
    if len(expr) == 1 and isColumnToken(expr[0]):
        col = expr[0]
        return col in alias_set or normalize([col]) in group_set

    return False


def isValidHavingRHS(expr, group_set, alias_set):
    """
    Validates the right-hand side of a HAVING comparison.

    Allowed:
    - aggregate expressions
    - grouped columns or aliases
    - numeric literals
    """
    expr = stripParens(expr)

    # Aggregate expression → valid
    if containsAggregate(expr):
        return True

    # Single column or alias → must be grouped or aliased
    if len(expr) == 1 and isColumnToken(expr[0]):
        key = normalize(expr)
        return key in group_set or expr[0] in alias_set

    # Numeric literal (optionally parenthesized)
    for tok in expr:
        if not (tok.isnumeric() or tok in {"(", ")"}):
            return False

    return True


def validateHavingExpr(tokens, group_set, alias_set):
    """
    Recursively validates a HAVING boolean expression.

    Rules enforced:
    - Boolean structure (AND / OR)
    - Valid comparison operators
    - Aggregates allowed
    - Non-aggregated columns must be grouped or aliased
    """
    tokens = stripParens(tokens)

    # Split on top-level logical operators
    parts = splitHavingExprs(tokens)

    # Recurse if multiple logical parts exist
    if len(parts) > 1:
        for part in parts:
            err = validateHavingExpr(part, group_set, alias_set)
            if err:
                return err
        return None

    # At this point, expression must be a single comparison
    lhs, op, rhs = splitComparison(tokens)

    if op is None:
        return {"error": "Invalid HAVING expression"}

    if not isValidHavingLHS(lhs, group_set, alias_set):
        return {"error": "Invalid HAVING expression"}

    if not isValidHavingRHS(rhs, group_set, alias_set):
        return {"error": "Invalid HAVING comparison value"}

    return None
