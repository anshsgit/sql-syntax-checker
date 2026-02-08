from select.helper.havingChecksHelper import stripParens, normalize
from select.helper.whereChecksHelper import validateExpression
from select.helper.groupByChecksHelper import containsAggregate


def extractOrderBy(tokens):
    """
    Extracts ORDER BY clause tokens.
    Ensures ORDER is immediately followed by BY.
    Stops parsing at LIMIT.
    """
    if "order" not in tokens:
        return None

    i = tokens.index("order")
    if i + 1 >= len(tokens) or tokens[i + 1] != "by":
        return {"error": "ORDER must be followed by BY"}

    start = i + 2
    end = len(tokens)

    # ORDER BY ends when LIMIT begins
    for clause in ("limit",):
        if clause in tokens[start:]:
            end = tokens.index(clause)

    return tokens[start:end]


def splitOrderByItems(tokens):
    """
    Splits ORDER BY clause into individual items.
    Commas inside parentheses are ignored.
    """
    items = []
    depth = 0
    start = 0

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and tok == ",":
            items.append(tokens[start:i])
            start = i + 1

    items.append(tokens[start:])
    return items


def splitOrderItem(item):
    """
    Splits an ORDER BY item into:
      - expression
      - direction (ASC / DESC)

    Default direction is ASC.
    """
    if not item:
        return None, None

    if item[-1] in {"asc", "desc"}:
        return item[:-1], item[-1]

    return item, "asc"


def isValidOrderByExpr(tokens, select_set, alias_set, group_set):
    """
    Validates a single ORDER BY expression.

    Resolution priority:
    1. SELECT aliases
    2. SELECT expressions
    3. GROUP BY expressions
    4. Any valid SQL expression
    """

    if not tokens:
        return False, "Empty ORDER BY expression"

    expr = tokens

    # Direction keyword must appear last
    if tokens[-1] in {"asc", "desc"}:
        expr = tokens[:-1]

    if not expr:
        return False, "ORDER BY expression missing before direction"

    # Normalize expression for comparison
    expr = stripParens(expr)
    key = normalize(expr)

    # 1️⃣ Alias reference (always allowed)
    if key in alias_set:
        return True, None

    # 2️⃣ Expression appears directly in SELECT
    if key in select_set:
        return True, None

    # 3️⃣ GROUP BY expression
    if group_set and key in group_set:
        return True, None

    # 4️⃣ Allow any syntactically valid expression (SQL-like behavior)
    err = validateExpression(expr, "order")
    if err:
        return False, "Invalid ORDER BY expression"

    # 5️⃣ Aggregates must be present in SELECT or GROUP BY
    if containsAggregate(expr):
        return False, "Aggregate in ORDER BY must appear in SELECT or GROUP BY"

    return True, None
