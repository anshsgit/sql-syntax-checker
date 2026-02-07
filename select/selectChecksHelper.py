from select.utils import isQualifiedColumnAt, consumeAggregate, SQL_KEYWORDS, AGG_FUNCS, isColumnToken
from select.whereChecksHelper import validateExpression

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



def consumeExpr(tokens, i):
    if tokens[i] != "(":
        return None
    
    depth = 1
    j = i + 1

    while j < len(tokens) and depth > 0:
        if tokens[j] == '(':
            depth += 1
        elif tokens[j] == ')':
            depth -= 1
        j += 1
    
    if depth != 0:
        return None
    
    inner = tokens[i+1: j-1]
    return j, inner



def handleSelectOrder(selectList):
    if not selectList:
        return None

    if selectList[0] == ",":
        return {"error": "SELECT cannot start with a comma"}

    if selectList[-1] == ",":
        return {"error": "SELECT cannot end with a comma"}

    state = "EXPECT_COLUMN"   
    alias_used = False

    i = 0
    while i < len(selectList):
        tok = selectList[i]


        if state == "EXPECT_COLUMN":

            if tok == "(":
                res = consumeExpr(selectList, i)
                if res is None:
                    return {"error": "Unmatched parenthesis in SELECT expression"}
                
                end, inner = res

                if not inner:
                    return {"error": "Empty expression in select"}
                
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

                err = validateExpression(inner, "select")
                if err:
                    return {
                        "error": "Invalid expression inside aggregate function",
                        "function": tok,
                        "details": err
                    }

                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i = end
                continue


            # qualified column: s . name
            if isQualifiedColumnAt(selectList, i):
                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i += 3
                continue  

            # normal column
            if tok == "*" or isColumnToken(tok):
                state = "EXPECT_ALIAS_OR_COMMA"
                alias_used = False
                i += 1
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
                i += 1
                continue
            if tok == ",":
                state = "EXPECT_COLUMN"
                i += 1
                continue
            return {
                "error": "Missing comma between column expressions",
                "position": i
            }


        if state == "EXPECT_ALIAS_NAME":
            if isColumnToken(tok):
                state = "EXPECT_ALIAS_OR_COMMA"
                i += 1
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


def collectQualifiedColumns(selectedList, unresolved):
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
                "column": selectedList[i+ 2],
                "position": i
            })        
            i += 3
            continue
        i += 1