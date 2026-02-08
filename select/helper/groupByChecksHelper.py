from select.helper.selectChecksHelper import containsAggregate


def normalize(expr):
    """
    Normalize an expression for comparison:
    - Removes redundant outer parentheses
    - Converts token list into a comparable string form

    Used to compare SELECT and GROUP BY expressions reliably.
    """
    expr = expr[:]

    # Strip redundant outer parentheses
    while expr and expr[0] == "(" and expr[-1] == ")":
        depth = 0
        valid = True

        for i, tok in enumerate(expr):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1

            # If outer parentheses close before the end,
            # they are not redundant
            if depth == 0 and i < len(expr) - 1:
                valid = False
                break

        if not valid:
            break

        # Remove one layer of parentheses
        expr = expr[1:-1]

    # Convert normalized token list to string
    return " ".join(expr)


def splitSelectExpressions(selectList):
    """
    Splits SELECT list into individual expressions.
    Commas inside parentheses are ignored.
    """
    exprs = []
    depth = 0
    start = 0

    for i, tok in enumerate(selectList):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif tok == "," and depth == 0:
            if start == i:
                return None, {"error": "Empty SELECT expression"}
            exprs.append(selectList[start:i])
            start = i + 1

    # Trailing comma check
    if start >= len(selectList):
        return None, {"error": "Empty SELECT expression"}

    exprs.append(selectList[start:])
    return exprs, None


def stripAlias(expr):
    """
    Removes explicit alias from a SELECT expression.
    Only strips top-level AS aliases.
    """
    depth = 0
    for i, tok in enumerate(expr):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # Alias must be top-level
        if depth == 0 and tok == "as":
            return expr[:i]

    return expr


def extractGroupByList(tokens):
    """
    Extracts GROUP BY clause tokens.
    Stops when HAVING, ORDER, or LIMIT begins.
    """
    if "group" not in tokens:
        return None

    i = tokens.index("group")
    if i + 1 >= len(tokens) or tokens[i + 1] != "by":
        return {"error": "GROUP must be followed by BY"}

    start = i + 2
    end = len(tokens)

    for clause in ("having", "order", "limit"):
        if clause in tokens[start:]:
            end = tokens.index(clause)
            break

    return tokens[start:end]


def splitGroupByExpressions(tokens):
    """
    Splits GROUP BY clause into individual expressions.
    Commas inside parentheses are ignored.
    """
    exprs = []
    depth = 0
    start = 0

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif tok == "," and depth == 0:
            if start == i:
                return None, {"error": "Empty GROUP BY expression"}
            exprs.append(tokens[start:i])
            start = i + 1

    # Trailing comma check
    if start >= len(tokens):
        return None, {"error": "Empty GROUP BY expression"}

    exprs.append(tokens[start:])
    return exprs, None

def isScalarSubquery(expr):
    """
    Returns True if the SELECT expression is a scalar subquery.
    Example: (SELECT MIN(b) FROM t)
    """
    return (
        expr
        and expr[0] == "("
        and len(expr) > 1
        and expr[1] == "select"
    )


def validateGroupBy(selectExprs, groupExprs):
    """
    Enforces strict SQL GROUP BY rules:
    - GROUP BY cannot contain aggregates
    - GROUP BY expressions must exactly match
      non-aggregated SELECT expressions
    """

    # normalize expressions
    select_norm = []
    for expr in selectExprs:

        # 🔥 ignore scalar subqueries for GROUP BY rules
        if isScalarSubquery(expr):
            continue

        if not containsAggregate(expr):
            select_norm.append(normalize(expr))

    group_norm = [normalize(expr) for expr in groupExprs]

    # 1️⃣ No aggregates in GROUP BY
    for expr in groupExprs:
        if containsAggregate(expr):
            return {
                "error": "Aggregate functions are not allowed in GROUP BY"
            }

    # 2️⃣ Exact match required
    if set(select_norm) != set(group_norm):
        return {
            "error": "GROUP BY expressions must exactly match non-aggregated SELECT expressions",
            "select": select_norm,
            "group_by": group_norm,
        }

    return None
