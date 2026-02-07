def extractFromList(tokens):
    if "from" not in tokens:
        return None

    start = tokens.index("from") + 1
    
    for clause in ("where", "group", "order", "having", "limit"):
        if clause in tokens[start:]:
            end = tokens.index(clause)
            return tokens[start:end]
    
    return tokens[start:]


def splitRef(tokens):

    refs = []
    depth = 0
    start = 0

    for i, tok in enumerate(tokens):
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
        elif tok == ',' and depth == 0:
            refs.append(tokens[start:i])
            start = i+1
    
    refs.append(tokens[start:])
    return refs


def validateTableRef(tokens):

    if not tokens:
        return {"error": "Empty table reference"}
    
    i = 0

    if i >= len(tokens) or not tokens[i].isidentifier():
        return {"error": "Invalid table name"}
    
    table = tokens[i]
    i += 1

    if i + 1 < len(tokens) and tokens[i] == ".":
        if not tokens[i+1].isidentifier():
            return {"error": "invalid table name"}
        table = f"{table}.{tokens[i+1]}"
        i += 2

    
    if i < len(tokens) and tokens[i] == 'as':
        i += 1

    alias = None
    if i < len(tokens):
        if not tokens[i].isidentifier():
            return {"error": "Invalid alias"}
        alias = tokens[i]
        i += 1
    
    if i != len(tokens):
        return {"error": "unexpected tokens in table ref"}
    if alias == table:
        return {
            "error": "table alias cannot be same as table name",
            "table": table
        }
    return {
        "table": table,
        "alias": alias or table
    }
