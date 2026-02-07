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
