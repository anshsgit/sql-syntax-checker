from select.utils import isColumnToken

LOGICAL_OPS = {"and", "or"}
COMPARISON_OPS = {"=", "!=", "<", ">", "<=", ">="}
ARITHMETIC_OPS = {"+", "-", "*", "/"}

def extractConditions(tokens):
    if "where" not in tokens:
        return None
    
    start = tokens.index("where") + 1

    for clause in ('group', 'order', 'limit', 'having'):
        if clause in tokens[start:]:
            end = tokens.index(clause)
            return tokens[start:end]

    return tokens[start:]

def checkParentheses(tokens):

    depth = 0
    for tok in tokens:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
            if depth < 0:
                return {"error": "Unmatched closing parenthesis"}
    if depth != 0:
        return {"error": "Unmatched opening parenthesis"}
    return None

def stripOuterParens(tokens):
    while tokens and tokens[0] == "(" and tokens[-1] == ")":
        depth = 0
        valid = True
        for i, tok in enumerate(tokens):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1
            if depth == 0 and i < len(tokens) - 1:
                valid = False
                break
        if valid:
            tokens = tokens[1:-1]
        else:
            break
    return tokens

def validateBooleanExpr(tokens):
    tokens = stripOuterParens(tokens)

    if not tokens:
        return {"error": "Empty expression"}

    depth = 0

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        # split ONLY on top-level AND / OR
        elif depth == 0 and tok in LOGICAL_OPS:
            left = tokens[:i]
            right = tokens[i+1:]
            if not left or not right:
                return {"error": "Logical operator without operand"}

            err = validateBooleanExpr(left)
            if err:
                return err

            err = validateBooleanExpr(right)
            if err:
                return err

            return None   # both sides valid

    # no AND / OR at top-level → must be a comparison
    return validateComparison(tokens)

def validateComparison(tokens):
    depth = 0
    op_index = None
    op = None

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        elif depth == 0 and isOperatorLike(tok):
            if tok not in COMPARISON_OPS:
                return {
                    "error": f"Invalid comparator: {tok}"
                }
            if op is not None:
                return {"error": "Multiple comparison operators"}
            op = tok
            op_index = i

    if op is None:
        return {"error": "Missing comparison operator"}

    lhs = stripOuterParens(tokens[:op_index])
    rhs = stripOuterParens(tokens[op_index + 1:])

    if not lhs or not rhs:
        return {"error": "Incomplete comparison"}

    err = validateExpression(lhs)
    if err:
        return err

    err = validateExpression(rhs)
    if err:
        return err

    return None


OP_CHARS = set("<>!=")
def isOperatorLike(tok):
    return all(c in OP_CHARS for c in tok)

def validateExpression(tokens):
    if not tokens:
        return {"error": "Empty expression"}

    tokens = stripOuterParens(tokens)

    expecting_operand = True
    i = 0

    while i < len(tokens):
        tok = tokens[i]

        if expecting_operand:
            # ---- parenthesized sub-expression ----
            if tok == "(":
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j] == "(":
                        depth += 1
                    elif tokens[j] == ")":
                        depth -= 1
                    j += 1

                if depth != 0:
                    return {"error": "Unmatched parenthesis in expression"}

                # recursively validate inside parentheses
                inner = tokens[i + 1 : j - 1]
                err = validateExpression(inner)
                if err:
                    return err

                expecting_operand = False
                i = j
                continue

            # ---- normal operand ----
            if isColumnToken(tok) or tok.isnumeric():
                expecting_operand = False
                i += 1
                continue

            return {
                "error": "Expected operand in expression",
                "position": i,
                "token": tok
            }

        else:
            if tok in ARITHMETIC_OPS:
                expecting_operand = True
                i += 1
                continue

            return {
                "error": "Expected arithmetic operator",
                "position": i,
                "token": tok
            }

    if expecting_operand:
        return {"error": "Expression cannot end with operator"}

    return None



