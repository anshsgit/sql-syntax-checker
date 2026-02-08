# Defines the correct order of SQL clauses.
# Lower number = earlier in the query.
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
    """
    Scans a list of SQL tokens and extracts top-level clauses
    along with their positions.
    """
    clauses = []
    i = 0
    depth = 0  # Tracks parentheses nesting level

    while i < len(tokens):
        tok = tokens[i]

        # Entering parentheses increases depth
        if tok == "(":
            depth += 1
            i += 1
            continue

        # Exiting parentheses decreases depth
        elif tok == ")":
            depth -= 1
            i += 1
            continue

        # Ignore tokens inside parentheses (subqueries, expressions)
        if depth != 0:
            i += 1
            continue

        # Detect multi-word GROUP BY clause
        if tok == "group" and i + 1 < len(tokens) and tokens[i + 1] == "by":
            clauses.append(("group by", i))
            i += 2
            continue

        # Detect multi-word ORDER BY clause
        if tok == "order" and i + 1 < len(tokens) and tokens[i + 1] == "by":
            clauses.append(("order by", i))
            i += 2
            continue

        # Detect single-word clauses (SELECT, FROM, WHERE, etc.)
        if tok in clauseOrder:
            clauses.append((tok, i))
            i += 1
            continue

        i += 1

    return clauses


def checkOrder(clauses):
    """
    Ensures clauses appear in valid SQL order.
    """
    last = 0  # Tracks the last seen clause order value

    for name, pos in clauses:
        current = clauseOrder[name]

        # If a clause appears earlier than allowed, report an error
        if current < last:
            return {
                "error": "Clause Order Error",
                "clause": name,
                "position": pos,
                "why": f"'{name}' appears in the wrong order"
            }

        last = current

    return None


def checkMandatoryClauses(clauses):
    """
    Verifies required SQL clauses and logical dependencies.
    """
    mandatory = {"select", "from"}
    found = {name for name, _ in clauses}

    # Check for missing mandatory clauses
    missing = mandatory - found
    if missing:
        return {
            "error": "Missing Mandatory Clause",
            "missing": sorted(missing)
        }

    # HAVING must be used only with GROUP BY
    if "having" in found and "group by" not in found:
        return {
            "error": "HAVING without GROUP BY"
        }

    return None


def checkDuplicateClauses(clauses):
    """
    Detects duplicate SQL clauses.
    """
    seen = {}

    for name, pos in clauses:
        # If clause was already seen, report duplication
        if name in seen:
            return {
                "error": "Duplicate Clause",
                "clause": name,
                "first_at": seen[name],
                "again_at": pos,
                "why": f"'{name}' clause appears more than once."
            }

        # Record first occurrence position
        seen[name] = pos

    return None
