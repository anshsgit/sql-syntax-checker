SQL_KEYWORDS = {
    "select", "from", "where", "group", "by",
    "having", "order", "limit", "as"
}

AGG_FUNCS = {"sum", "count", "avg", "min", "max"}


def isColumnToken(tok):
    return (
        tok.isidentifier()
        and tok not in SQL_KEYWORDS
        and tok not in AGG_FUNCS
    )

def isQualifiedColumnAt(tokens, i):
    return (
        i + 2 < len(tokens)
        and isColumnToken(tokens[i])
        and tokens[i + 1] == "."
        and isColumnToken(tokens[i + 2])
    )

def consumeAggregate(tokens, i):
    """
    Assumes tokens[i] is an aggregate function name.
    Returns (end_index, inner_tokens) or None on error.
    """
    if i + 1 >= len(tokens) or tokens[i + 1] != "(":
        return None

    depth = 1
    j = i + 2

    while j < len(tokens) and depth > 0:
        if tokens[j] == "(":
            depth += 1
        elif tokens[j] == ")":
            depth -= 1
        j += 1

    if depth != 0:
        return None

    inner = tokens[i + 2 : j - 1]
    return j, inner

def extractLimit(tokens):
    if "limit" not in tokens:
        return None

    i = tokens.index("limit")
    start = i + 1
    end = len(tokens)

    return tokens[start:end]
