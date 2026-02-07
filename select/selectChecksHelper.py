from select.utils import SQL_KEYWORDS, AGG_FUNCS, isColumnToken


def extractSelectList(tokens):
    try:
        start = tokens.index("select") + 1
        end = tokens.index("from")
    except ValueError:
        return None
    return tokens[start:end]


def checkColumnNames(selectList):
    for tok in selectList:
        if isColumnToken(tok) and tok in SQL_KEYWORDS:
            return {
                "error": "Invalid column name",
                "name": tok
            }
    return None


def checkStarUsage(selectList):
    depth = 0
    top_level_star = False
    top_level_items = 0

    for tok in selectList:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

    
        if depth == 0 and (isColumnToken(tok) or tok == "*" or tok in AGG_FUNCS):
            top_level_items += 1
            if tok == "*":
                top_level_star = True

    if top_level_star and top_level_items > 1:
        return {
            "error": "Invalid * usage",
            "why": "* cannot be combined with other columns"
        }

    return None



def handleSelectOrder(selectList):
    if not selectList:
        return None

    if selectList[0] == ",":
        return {"error": "SELECT cannot start with a comma"}

    if selectList[-1] == ",":
        return {"error": "SELECT cannot end with a comma"}

    depth = 0
    state = "EXPECT_COLUMN"   
    alias_used = False

    for i, tok in enumerate(selectList):

        if tok == "(":
            depth += 1
            continue
        elif tok == ")":
            depth -= 1
            continue

        if depth != 0:
            continue  


        if state == "EXPECT_COLUMN":
            if tok == "*" or tok in AGG_FUNCS or isColumnToken(tok):
                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                continue
            return {"error": f"Expected column at position {i}"}



        if state == "EXPECT_ALIAS_OR_COMMA":
            if tok == "as":
                if alias_used:
                    return {
                        "error": "Multiple aliases for the same column"
                    }
                alias_used = True
                state = "EXPECT_ALIAS_NAME"
                continue
            if tok == ",":
                state = "EXPECT_COLUMN"
                continue
            return {
                "error": "Missing comma between column expressions",
                "position": i
            }


        if state == "EXPECT_ALIAS_NAME":
            if isColumnToken(tok):
                state = "EXPECT_ALIAS_OR_COMMA"
                continue
            return {
                "error": "Invalid alias name",
                "position": i
            }

    if state == "EXPECT_COLUMN":
        return {"error": "Trailing comma in SELECT list"}

    return None



def checkAggregateFunctions(selectList):
    i = 0
    while i < len(selectList):
        tok = selectList[i]

        if tok in AGG_FUNCS:
            if i + 1 >= len(selectList) or selectList[i + 1] != "(":
                return {
                    "error": "Aggregate function error",
                    "function": tok
                }

            depth = 0
            j = i
            while j < len(selectList):
                if selectList[j] == "(":
                    depth += 1
                elif selectList[j] == ")":
                    depth -= 1
                j += 1

            if depth != 0:
                return {
                    "error": "aggregate function not opened or closed properly",
                    "function": tok
                }

            i = j
        i += 1

    return None


# def checkAliases(selectList):
#     i = 0
#     while i < len(selectList):
#         if selectList[i] == "as":
#             if i + 1 >= len(selectList) or (i+1 <= len(selectList) and selectList[i+1] == ','):
#                 return {
#                     "error": "Alias error",
#                     "why": "AS must be followed by an alias"
#                 }
#             alias = selectList[i + 1]
#             if alias in SQL_KEYWORDS:
#                 return {
#                     "error": "Invalid alias",
#                     "alias": alias
#                 }
#             i += 1
#         i += 1
#     return None


def extractAliases(selectList):
    aliases = {}
    depth = 0
    i = 0

    while i < len(selectList):
        tok = selectList[i]

        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        if depth == 0:

            # explicit alias: expr AS alias
            if tok == "as":
                alias = selectList[i + 1]

                expr_end = i - 1
                expr_start = expr_end
                while expr_start >= 0 and selectList[expr_start] != "," and selectList[expr_start] != 'select':
                    expr_start -= 1
                expr_start += 1

                aliases[alias] = selectList[expr_start:expr_end + 1]
                i += 2
                continue

        i += 1

    return aliases


