from select.helper.whereChecksHelper import validateBooleanExpr


# JOIN-related keywords
JOIN_TOKENS = {"join", "inner", "left", "right", "full"}

# Tokens that can start a JOIN chain
JOIN_STARTERS = JOIN_TOKENS | {","}


def containsJoin(tokens):
    """
    Returns True if explicit JOIN syntax is used anywhere.
    """
    return any(tok in JOIN_TOKENS for tok in tokens)


def extractFromList(tokens):
    """
    Extract FROM clause tokens, stopping at OUTER clauses only.
    """
    if "from" not in tokens:
        return None

    depth = 0
    start = None

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # 🔥 detect OUTER FROM only
        if depth == 0 and tok == "from":
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

        # 🔥 stop only at OUTER clause boundaries
        if depth == 0 and tok in {"where", "group", "having", "order", "limit"}:
            end = i
            break

    return tokens[start:end]



def splitRef(tokens):
    """
    Splits comma-separated table references at top level only.
    Parenthesized expressions are ignored.
    """
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
            start = i + 1

    refs.append(tokens[start:])
    return refs


def validateTableRef(tokens):
    """
    Validates a single table reference.
    Syntax supported:
      table
      schema.table
      table [AS] alias
      schema.table [AS] alias
    """
    if not tokens:
        return {"error": "Empty table reference"}

    i = 0

    # ---- base table name ----
    if not tokens[i].isidentifier():
        return {
            "error": "Invalid table name",
            "token": tokens[i]
        }

    table = tokens[i]
    i += 1

    # ---- optional schema qualification ----
    if i + 1 < len(tokens) and tokens[i] == ".":
        if not tokens[i + 1].isidentifier():
            return {"error": "Invalid schema-qualified table name"}
        table = f"{table}.{tokens[i + 1]}"
        i += 2

    # ---- optional AS keyword ----
    if i < len(tokens) and tokens[i] == "as":
        i += 1

    # ---- optional alias ----
    alias = None
    if i < len(tokens):
        if not tokens[i].isidentifier():
            return {
                "error": "Invalid table alias",
                "token": tokens[i]
            }
        alias = tokens[i]
        i += 1

    # ---- reject trailing garbage ----
    if i != len(tokens):
        return {
            "error": "Unexpected tokens in table reference",
            "tokens": tokens[i:]
        }

    # ---- alias cannot shadow table name ----
    if alias == table:
        return {
            "error": "Table alias cannot be same as table name",
            "table": table
        }

    return {
        "table": table,
        "alias": alias or table
    }


def has_top_level_commas(tokens):
    """
    Detects comma joins at top level (not inside parentheses).
    """
    depth = 0
    for tok in tokens:
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
        elif tok == ',' and depth == 0:
            return True
    
    return False


def collect_on_aliases(tokens):
    """
    Collects table aliases referenced in ON conditions.
    Detects patterns like alias.column
    """
    aliases = set()
    i = 0
    while i < len(tokens):
        if (
            i + 2 < len(tokens)
            and tokens[i].isidentifier()
            and tokens[i + 1] == "."
            and tokens[i + 2].isidentifier()
        ):
            aliases.add(tokens[i])
            i += 3
        else:
            i += 1
    return aliases


def validateJoinChain(tokens, self):
    """
    Validates FROM clause containing JOIN chains.

    Rules enforced:
    - Cannot mix comma joins with explicit JOIN syntax
    - Validates each table reference
    - Ensures JOIN has an ON clause
    - Validates ON condition syntax
    - Ensures ON clause uses only known table aliases
    """
    i = 0
    n = len(tokens)

    # ---- detect mixed join styles ----
    if has_top_level_commas(tokens) and containsJoin(tokens):
        return {
            "error": "Cannot mix comma joins with explicit JOIN syntax",
            "hint": "Use JOIN ... ON everywhere or commas everywhere"
        }

    # ---- parse base table ----
    base = []
    while i < n and tokens[i] not in JOIN_TOKENS:
        base.append(tokens[i])
        i += 1

    base_ref = validateTableRef(base)
    if "error" in base_ref:
        base_ref["context"] = "FROM base table"
        return base_ref

    # Initialize table alias registry
    self.from_tables = {}
    self.from_tables[base_ref["alias"]] = base_ref["table"]

    # ---- JOIN processing loop ----
    while i < n:

        # ---- JOIN keyword handling ----
        tok = tokens[i]
        if tok == "join":
            i += 1
        elif tok in {"inner", "left", "right", "full"}:
            if i + 1 < n and tokens[i + 1] == "join":
                i += 2
            else:
                return {
                    "error": "Invalid JOIN syntax",
                    "token": tok
                }
        else:
            return {
                "error": "Unexpected token in FROM clause",
                "token": tok
            }

        # ---- joined table reference ----
        join_ref = []
        while i < n and tokens[i] != "on":
            join_ref.append(tokens[i])
            i += 1

        if not join_ref:
            return {"error": "JOIN missing table reference"}

        result = validateTableRef(join_ref)
        if "error" in result:
            result["context"] = "JOIN table"
            return result

        alias = result["alias"]
        table = result["table"]

        # Prevent alias reuse
        if alias in self.from_tables:
            return {
                "error": "Duplicate table alias",
                "alias": alias
            }

        # ---- ON clause ----
        if i >= n or tokens[i] != "on":
            return {"error": "JOIN requires ON clause"}
        i += 1

        on_start = i
        depth = 0

        # Consume ON expression until next JOIN
        while i < n:
            if tokens[i] == "(":
                depth += 1
            elif tokens[i] == ")":
                depth -= 1
            elif depth == 0 and tokens[i] in JOIN_TOKENS:
                break
            i += 1

        on_tokens = tokens[on_start:i]
        if not on_tokens:
            return {"error": "Empty JOIN condition"}

        # ---- validate ON expression syntax ----
        err = validateBooleanExpr(on_tokens)
        if err:
            return {
                "error": "Invalid JOIN condition",
                "details": err
            }

        # ---- validate table aliases used in ON ----
        used_aliases = collect_on_aliases(on_tokens)
        allowed_aliases = set(self.from_tables.keys()) | {alias}

        for a in used_aliases:
            if a not in allowed_aliases:
                return {
                    "error": "Unknown table alias in JOIN condition",
                    "alias": a
                }

        # Register joined table
        self.from_tables[alias] = table

    return None
