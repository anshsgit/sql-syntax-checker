clauseOrder = {
    "select": 1,
    "from": 2,
    "where": 3,
    "group by": 4,
    "having": 5,
    "order by": 6,
    "limit": 7
}

def extractClauses(tokens):
    clauses = []
    i = 0

    while i < len(tokens):

        if tokens[i] == 'group' and i+1 < len(tokens) and tokens[i+1] == 'by':
            clauses.append(("group by", i))
            i += 2
        elif tokens[i] == 'order' and i + 1 < len(tokens) and tokens[i+1] == 'by':
            clauses.append(("order by", i))
            i += 2
        elif tokens[i] in clauseOrder:
            clauses.append((tokens[i], i))
            i += 1
        else:
            i += 1

    return clauses

def checkOrder(clauses):

    last = 0
    for name, pos in clauses:
        current = clauseOrder[name]
        if current < last:
            return {
                "error": "Clause Order Error",
                "where": name,
                "why": f"{name} appears in the wrong order.",
            }
        last = current
    return None


def checkMandatoryClauses(clauses):
    mandatory = {'select', 'from'}
    found = {name for name, _ in clauses}

    missing = mandatory - found
    if missing:
        return {
            "error": "Missing Mandatory Clause",
            "missing": list(missing),
            "why": f"Query must contain {', '.join(sorted(missing))} clause(s)."
        }

    if "having" in found and "group by" not in found:
        return {
            "error": "Having without group by",
        }

    return None

def checkDuplicateClauses(clauses):
    seen = {}

    for name, pos in clauses:
        if name in seen:
            return {
                "error": "Duplicate Clause",
                "clause": name,
                "first_at": seen[name],
                "again_at": pos,
                "why": f"'{name}' clause appears more than once."
            }
        seen[name] = pos
    
    print(seen)

    return None
