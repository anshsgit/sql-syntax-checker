from select.helper.utils import isQualifiedColumnAt, isColumnToken, consumeAggregate, AGG_FUNCS, isSubquery

# Logical operators for boolean expressions
LOGICAL_OPS = {"and", "or"}

# Comparison operators
COMPARISON_OPS = {"=", "!=", "<", ">", "<=", ">="}

# Arithmetic operators for expressions
ARITHMETIC_OPS = {"+", "-", "*", "/"}

# Characters that may appear in operator tokens
OP_CHARS = set("<>!=")


# Determines if a token visually resembles an operator.
# Full correctness is validated later.
def isOperatorLike(tok):
    return all(c in OP_CHARS for c in tok)


# Extracts tokens belonging to the WHERE clause.
# Stops when a later clause keyword is encountered.
def extractConditions(tokens):
    if "where" not in tokens:
        return None

    start = tokens.index("where") + 1

    # WHERE ends when another clause begins
    for clause in ('group', 'order', 'limit', 'having'):
        if clause in tokens[start:]:
            end = tokens.index(clause)
            return tokens[start:end]

    return tokens[start:]


# Ensures parentheses are balanced and correctly nested
def checkParentheses(tokens):
    depth = 0
    for tok in tokens:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
            # Closing before any opening
            if depth < 0:
                return {"error": "Unmatched closing parenthesis"}

    # Remaining unmatched opening parentheses
    if depth != 0:
        return {"error": "Unmatched opening parenthesis"}

    return None


# Removes redundant outer parentheses wrapping the entire expression
def stripOuterParens(tokens):
    while tokens and tokens[0] == "(" and tokens[-1] == ")":
        depth = 0
        valid = True

        # Verify that outer parentheses close at the very end
        for i, tok in enumerate(tokens):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1

            # If parentheses close early, they are not redundant
            if depth == 0 and i < len(tokens) - 1:
                valid = False
                break

        if valid:
            tokens = tokens[1:-1]
        else:
            break

    return tokens


# Validates boolean expressions with AND / OR and proper precedence
def validateBooleanExpr(tokens, clause="where"):
    tokens = stripOuterParens(tokens)
    if not tokens:
        return {"error": "Empty expression"}

    # BETWEEN and IN behave as comparisons, not logical splits
    if find_top_level(tokens, {"between", "in"}) is not None:
        return validateComparison(tokens, clause)

    # Split on top-level AND / OR
    idx = find_top_level(tokens, LOGICAL_OPS)
    if idx is not None:
        left = tokens[:idx]
        right = tokens[idx + 1:]

        if not left or not right:
            return {"error": "Logical operator without operand"}

        err = validateBooleanExpr(left, clause)
        if err:
            return err
        return validateBooleanExpr(right, clause)

    # No boolean operator → must be a comparison
    return validateComparison(tokens, clause)


# Finds the index of a target token at top-level (outside parentheses)
def find_top_level(tokens, targets):
    depth = 0
    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and tok in targets:
            return i
    return None


# Splits tokens by a separator, ignoring nested parentheses
def split_top_level(tokens, separator):
    parts = []
    depth = 0
    start = 0

    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif tok == separator and depth == 0:
            parts.append(tokens[start:i])
            start = i + 1

    parts.append(tokens[start:])
    return parts


# Routes comparison validation based on operator type
def validateComparison(tokens, clause):
    tokens = stripOuterParens(tokens)

    if find_top_level(tokens, {"in"}) is not None:
        return validateIn(tokens, clause)

    if find_top_level(tokens, {"between"}) is not None:
        return validateBetween(tokens, clause)

    return validateBinaryComparison(tokens, clause)


# Validates IN expressions: lhs IN (value1, value2, ...)
def validateIn(tokens, clause):
    idx = find_top_level(tokens, {"in"})
    if idx is None:
        return {"error": "Invalid IN expression"}

    # handle NOT IN
    if idx > 0 and tokens[idx - 1] == "not":
        lhs = tokens[:idx - 1]
    else:
        lhs = tokens[:idx]

    rhs = tokens[idx + 1:]

    if not lhs or not rhs:
        return {"error": "Incomplete IN expression"}

    # validate LHS first
    err = validateExpression(lhs, clause)
    if err:
        return err

    # RHS must be parenthesized
    if rhs[0] != "(" or rhs[-1] != ")":
        return {"error": "IN requires parenthesized list or subquery"}

    items = items = stripOuterParens(rhs[1:-1])
    if not items:
        return {"error": "IN list cannot be empty"}

    # ---- IN (subquery) ----
    if isSubquery(items):
        from select.selectParser import SelectParser
        from select.helper.selectChecksHelper import extractSelectList
        from select.helper.groupByChecksHelper import splitSelectExpressions

        parser = SelectParser()
        err = parser.analyse(items)
        if err:
            return {"error": "Invalid subquery in IN", "details": err}

        selectList = extractSelectList(items)
        exprs, err2 = splitSelectExpressions(selectList)
        if err2 or len(exprs) != 1:
            return {"error": "IN subquery must return exactly one column"}

        return None

    # ---- IN (value list) ----
    values = split_top_level(items, ",")

    for v in values:
        if not v:
            return {"error": "Empty value in IN list"}
        err = validateExpression(v, clause)
        if err:
            return err

    return None


# Validates BETWEEN expressions: lhs BETWEEN low AND high
def validateBetween(tokens, clause):
    idx = find_top_level(tokens, {"between"})
    lhs = tokens[:idx]
    rest = tokens[idx + 1:]

    if not lhs or not rest:
        return {"error": "Incomplete BETWEEN expression"}

    # BETWEEN requires a top-level AND
    and_idx = find_top_level(rest, {"and"})
    if and_idx is None:
        return {"error": "BETWEEN missing AND"}

    low = rest[:and_idx]
    high = rest[and_idx + 1:]

    if not low or not high:
        return {"error": "Incomplete BETWEEN bounds"}

    for part in (lhs, low, high):
        err = validateExpression(part, clause)
        if err:
            return err

    return None


# Validates binary comparisons like a = b or x >= y
def validateBinaryComparison(tokens, clause):
    depth = 0
    op = None
    op_index = None

    # Locate exactly one top-level comparison operator
    for i, tok in enumerate(tokens):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and isOperatorLike(tok):
            if tok not in COMPARISON_OPS:
                return {"error": f"Invalid comparator: {tok}"}
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

    err = validateExpression(lhs, clause)
    if err:
        return err
    return validateExpression(rhs, clause)



def validateScalarSubquery(tokens):
    from select.selectParser import SelectParser
    from select.helper.selectChecksHelper import extractSelectList
    from select.helper.groupByChecksHelper import splitSelectExpressions

    parser = SelectParser()
    err = parser.analyse(tokens)
    if err:
        return {"error": "Invalid subquery", "details": err}

    selectList = extractSelectList(tokens)
    exprs, err2 = splitSelectExpressions(selectList)
    if err2 or len(exprs) != 1:
        return {"error": "Subquery must return exactly one column"}

    return None

def consumeParenthesized(tokens, i):
    depth = 1
    j = i + 1

    while j < len(tokens) and depth > 0:
        if tokens[j] == "(":
            depth += 1
        elif tokens[j] == ")":
            depth -= 1
        j += 1

    if depth != 0:
        return None

    return j, stripOuterParens(tokens[i + 1 : j - 1])

def validateOperand(tokens, i, clause):
    tok = tokens[i]

    # Qualified column
    if isQualifiedColumnAt(tokens, i):
        return i + 3, None

    # Aggregate
    if tok in AGG_FUNCS:
        if clause == "where":
            return None, {"error": "Aggregate functions are not allowed in WHERE clause"}

        result = consumeAggregate(tokens, i)
        if result is None:
            return None, {"error": "Invalid aggregate function usage"}

        end, inner = result
        err = validateExpression(inner, clause)
        return (end, err)

    # Atomic
    if isColumnToken(tok) or tok.isnumeric():
        return i + 1, None

    return None, {
        "error": "Expected operand in expression",
        "position": i,
        "token": tok
    }

def validateArithmeticChain(tokens, clause):
    expecting_operand = True
    i = 0

    while i < len(tokens):
        if expecting_operand:
            # Parenthesized
            if tokens[i] == "(":
                res = consumeParenthesized(tokens, i)
                if res is None:
                    return {"error": "Unmatched parenthesis in expression"}

                j, inner = res

                # scalar subquery
                if inner and inner[0] == "select":
                    err = validateScalarSubquery(inner)
                    if err:
                        return err

                    # no arithmetic allowed after subquery
                    if j < len(tokens) and tokens[j] in ARITHMETIC_OPS:
                        return {"error": "Arithmetic on subquery is not allowed"}

                    i = j
                    expecting_operand = False
                    continue

                err = validateExpression(inner, clause)
                if err:
                    return err

                i = j
                expecting_operand = False
                continue

            # Normal operand
            nxt, err = validateOperand(tokens, i, clause)
            if err:
                return err

            i = nxt
            expecting_operand = False
            continue

        else:
            if tokens[i] in ARITHMETIC_OPS:
                expecting_operand = True
                i += 1
                continue

            return {
                "error": "Expected arithmetic operator",
                "position": i,
                "token": tokens[i]
            }

    if expecting_operand:
        return {"error": "Expression cannot end with operator"}

    return None

def validateExpression(tokens, clause):
    tokens = stripOuterParens(tokens)

    if not tokens:
        return {"error": "Empty expression"}

    # scalar subquery
    if tokens[0] == "select":
        return validateScalarSubquery(tokens)

    # SELECT *
    if len(tokens) == 1 and tokens[0] == "*":
        return None

    return validateArithmeticChain(tokens, clause)
