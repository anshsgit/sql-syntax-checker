from select.helper.utils import (
    isQualifiedColumnAt,
    consumeAggregate,
    SQL_KEYWORDS,
    AGG_FUNCS,
    isColumnToken,
)
from select.helper.whereChecksHelper import validateExpression
from select.helper.whereChecksHelper import ARITHMETIC_OPS


# ---------------------------------------------------------
# SELECT list extraction
# ---------------------------------------------------------

def extractSelectList(tokens):
    """
    Extract SELECT list tokens, stopping at the OUTER FROM.
    """
    if "select" not in tokens:
        return None

    i = tokens.index("select") + 1
    depth = 0
    select_list = []

    while i < len(tokens):
        tok = tokens[i]

        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # 🔥 stop only at OUTER FROM
        if depth == 0 and tok == "from":
            break

        select_list.append(tok)
        i += 1

    return select_list


# ---------------------------------------------------------
# Column name sanity checks
# ---------------------------------------------------------

def checkColumnNames(selectList):
    """
    Ensures column identifiers are not SQL keywords.
    """
    for tok in selectList:
        if isColumnToken(tok) and tok in SQL_KEYWORDS:
            return {
                "error": "Invalid column name",
                "name": tok
            }
    return None


# ---------------------------------------------------------
# '*' usage rules
# ---------------------------------------------------------

def checkStarUsage(selectList):
    """
    Enforces rules for '*' usage:
    - '*' must be the only top-level SELECT item
    - '*' inside expressions or arithmetic is allowed
    """
    depth = 0
    top_level_star = False
    top_level_items = 0

    i = 0
    while i < len(selectList):
        tok = selectList[i]

        # Track parentheses depth
        if tok == "(":
            depth += 1
            i += 1
            continue
        elif tok == ")":
            depth -= 1
            i += 1
            continue

        # Only consider top-level tokens
        if depth == 0:

            # ---- standalone SELECT * ----
            if (
                tok == "*" and
                (i == 0 or selectList[i - 1] == ",") and
                (i + 1 == len(selectList) or selectList[i + 1] == ",")
            ):
                top_level_star = True
                top_level_items += 1
                i += 1
                continue

            # ---- start of a top-level expression ----
            if isColumnToken(tok) or tok in AGG_FUNCS or tok.isnumeric():
                top_level_items += 1

                # Skip rest of the expression until comma
                j = i + 1
                inner_depth = 0
                while j < len(selectList):
                    if selectList[j] == "(":
                        inner_depth += 1
                    elif selectList[j] == ")":
                        inner_depth -= 1
                    elif selectList[j] == "," and inner_depth == 0:
                        break
                    j += 1

                i = j + 1 if j < len(selectList) else j
                continue

        i += 1

    if top_level_star and top_level_items > 1:
        return {
            "error": "Invalid * usage",
            "why": "* cannot be combined with other columns"
        }

    return None



# ---------------------------------------------------------
# Parenthesized expression consumer
# ---------------------------------------------------------

def consumeExpr(tokens, i):
    """
    Consumes a balanced parenthesized expression starting at index i.
    Returns (end_index, inner_tokens, is_subquery)
    """
    if tokens[i] != "(":
        return None

    depth = 1
    j = i + 1

    while j < len(tokens) and depth > 0:
        if tokens[j] == "(":
            depth += 1
        elif tokens[j] == ")":
            depth -= 1
        j += 1

    # Unbalanced parentheses
    if depth != 0:
        return None

    inner = tokens[i + 1 : j - 1]

    # 🔥 detect scalar subquery
    is_subquery = bool(inner and inner[0] == "select")

    return j, inner, is_subquery



# ---------------------------------------------------------
# SELECT list order + semantic validation
# ---------------------------------------------------------

def containsAggregate(tokens):
    """
    Checks whether a token list contains an aggregate call.
    Used to prevent nested aggregates.
    """
    for i, tok in enumerate(tokens):
        if tok in AGG_FUNCS and i + 1 < len(tokens) and tokens[i + 1] == "(":
            return True
    return False


def consumeSelectExpression(tokens, i):
    """
    Consumes a full SELECT expression up to a top-level comma.
    Validates the expression semantically.
    """
    depth = 0
    start = i

    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif tok == "," and depth == 0:
            break
        i += 1

    expr = tokens[start:i]
    if not expr:
        return None, {"error": "Empty SELECT expression"}

    err = validateExpression(expr, "select")
    if err:
        return None, err

    return i, expr


def handleSelectOrder(selectList):
    """
    Validates SELECT list structure:
    - Expression ordering
    - Alias rules
    - Comma placement
    - Aggregate correctness
    """
    if not selectList:
        return None

    if selectList[0] == ",":
        return {"error": "SELECT cannot start with a comma"}

    if selectList[-1] == ",":
        return {"error": "SELECT cannot end with a comma"}

    state = "EXPECT_COLUMN"
    alias_used = False
    aggregate_depth = 0   # Tracks nested aggregate context (defensive)

    i = 0
    while i < len(selectList):
        tok = selectList[i]

        if tok == "from":
            break


        # -------------------------
        # Expecting an expression
        # -------------------------

        # res = consumeSelectExpression(selectList, i)
        # if res:
        #     end, expr = res
        #     state = "EXPECT_ALIAS_OR_COMMA"
        #     alias_used = False
        #     i = end
        #     continue

        if state == "EXPECT_COLUMN":

            # ---- parenthesized expression ----
            if tok == "(":
                res = consumeExpr(selectList, i)

                if res is None:
                    return {"error": "Unmatched parenthesis in SELECT expression"}

                end, inner, is_subquery = res
                # print(is_subquery)
                # print(inner)
                if not inner:
                    return {"error": "Empty expression in SELECT"}
                
                if is_subquery:
                    from select.selectParser import SelectParser
                    parser = SelectParser()
                    err = parser.analyse(inner)
                    if err:
                        return {"error": "Invalid subquery", "details": err}

                    # scalar subquery is a valid SELECT item
                    state = "EXPECT_ALIAS_OR_COMMA"
                    i = end
                    continue


                err = validateExpression(inner, "select")
                if err:
                    return {
                        "error": "Invalid expression in SELECT",
                        "details": err
                    }

                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i = end
                continue

            # ---- aggregate function ----
            if tok in AGG_FUNCS:
                result = consumeAggregate(selectList, i)
                if result is None:
                    return {
                        "error": "Invalid aggregate function usage",
                        "function": tok
                    }

                end, inner = result

                if not inner:
                    return {
                        "error": "Empty expression inside aggregate function",
                        "function": tok
                    }

                # Prevent nested aggregates
                if containsAggregate(inner):
                    return {
                        "error": "Nested aggregate functions are not allowed",
                        "function": tok
                    }

                err = validateExpression(inner, "select")
                if err:
                    return {
                        "error": "Invalid expression inside aggregate function",
                        "function": tok,
                        "details": err
                    }

                aggregate_depth -= 1

                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i = end
                continue

            # ---- qualified column (table.column) ----
            if isQualifiedColumnAt(selectList, i):
                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i += 3
                continue

            # ---- simple column or '*' ----
            # ---- simple column or '*' ----
            if tok == "*" or isColumnToken(tok):
                i += 1

                # 🔥 NEW: allow arithmetic continuation
                while i < len(selectList):
                    if selectList[i] in ARITHMETIC_OPS:
                        i += 1
                        continue
                    if (
                        selectList[i] == "("
                        or isColumnToken(selectList[i])
                        or selectList[i].isnumeric()
                    ):
                        i += 1
                        continue
                    break

                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                continue


            return {"error": f"Expected column or expression at position {i}"}

        # -------------------------
        # Expecting alias or comma
        # -------------------------
        if state == "EXPECT_ALIAS_OR_COMMA":

            # explicit alias using AS
            if tok == "as":
                if alias_used:
                    return {"error": "Multiple aliases for the same column"}
                alias_used = True
                state = "EXPECT_ALIAS_NAME"
                i += 1
                continue

            # implicit alias (column-name style)
            if isColumnToken(tok) and tok not in SQL_KEYWORDS:
                if alias_used:
                    return {"error": "Multiple aliases for the same column"}
                alias_used = True
                i += 1
                continue

            # separator between expressions
            if tok == ",":
                state = "EXPECT_COLUMN"
                i += 1
                continue

            return {
                "error": "Missing comma between SELECT expressions",
                "position": i
            }

        # -------------------------
        # Expecting alias name
        # -------------------------
        if state == "EXPECT_ALIAS_NAME":
            if isColumnToken(tok) and tok not in SQL_KEYWORDS:
                state = "EXPECT_ALIAS_OR_COMMA"
                i += 1
                continue

            return {
                "error": "Invalid alias name",
                "position": i
            }

    # Dangling comma case
    if state == "EXPECT_COLUMN":
        return {"error": "Trailing comma in SELECT list"}

    return None


# ---------------------------------------------------------
# Aggregate syntax sanity (lightweight)
# ---------------------------------------------------------

def checkAggregateFunctions(selectList):
    """
    Ensures aggregate functions are immediately followed by '('.
    """
    i = 0
    while i < len(selectList):
        tok = selectList[i]

        if tok in AGG_FUNCS:
            if i + 1 >= len(selectList) or selectList[i + 1] != "(":
                return {
                    "error": "Aggregate function missing parentheses",
                    "function": tok
                }

        i += 1

    return None


# ---------------------------------------------------------
# Alias extraction
# ---------------------------------------------------------

def extractAliases(selectList):
    """
    Extracts explicit AS aliases from the SELECT list.
    Returns a mapping: alias -> expression tokens.
    """
    aliases = {}
    depth = 0
    i = 0

    while i < len(selectList):
        tok = selectList[i]

        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # Only process top-level aliases
        if depth == 0 and tok == "as":
            alias = selectList[i + 1]

            if not isColumnToken(alias):
                return {
                    "error": "Invalid alias name",
                    "name": alias
                }

            # Walk backwards to find expression start
            expr_end = i - 1
            expr_start = expr_end
            while expr_start >= 0 and selectList[expr_start] not in {",", "select"}:
                expr_start -= 1
            expr_start += 1

            aliases[alias] = selectList[expr_start:expr_end + 1]
            i += 2
            continue

        i += 1

    return aliases


# ---------------------------------------------------------
# Qualified column collection
# ---------------------------------------------------------

def collectQualifiedColumns(selectedList, unresolved):
    """
    Collects fully-qualified columns (table.column) at top level.
    Appends unresolved references for later resolution.
    """
    depth = 0
    i = 0

    while i < len(selectedList):
        tok = selectedList[i]

        if tok == "(":
            depth += 1
            i += 1
            continue
        elif tok == ")":
            depth -= 1
            i += 1
            continue

        if depth == 0 and isQualifiedColumnAt(selectedList, i):
            unresolved.append({
                "alias": selectedList[i],
                "column": selectedList[i + 2],
                "position": i
            })
            i += 3
            continue

        i += 1
