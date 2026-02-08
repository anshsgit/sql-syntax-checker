from select.helper.utils import isQualifiedColumnAt, isColumnToken, consumeAggregate, AGG_FUNCS

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
    lhs = tokens[:idx]
    rhs = tokens[idx + 1:]

    if not lhs or not rhs:
        return {"error": "Incomplete IN expression"}

    # RHS must be parenthesized
    if rhs[0] != "(" or rhs[-1] != ")":
        return {"error": "IN requires parenthesized list"}

    items = rhs[1:-1]
    if not items:
        return {"error": "IN list cannot be empty"}

    values = split_top_level(items, ",")

    # Validate each value expression
    for v in values:
        if not v:
            return {"error": "Empty value in IN list"}
        err = validateExpression(v, "where")
        if err:
            return err

    return validateExpression(lhs, clause)


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


# Validates arithmetic and atomic expressions
def validateExpression(tokens, clause):

    # Allow SELECT *
    if len(tokens) == 1 and tokens[0] == '*':
        return None
    
    tokens = stripOuterParens(tokens)
    if not tokens:
        return {"error": "Empty expression"}

    expecting_operand = True
    i = 0

    while i < len(tokens):
        tok = tokens[i]

        if expecting_operand:

            # Parenthesized sub-expression
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

                inner = tokens[i + 1 : j - 1]
                err = validateExpression(inner, clause)
                if err:
                    return err

                expecting_operand = False
                i = j
                continue

            # Qualified column reference (table.column)
            if isQualifiedColumnAt(tokens, i):
                expecting_operand = False
                i += 3
                continue

            # Aggregate function as operand
            if tok in AGG_FUNCS:
                if clause == 'where':
                    return {
                        "error": "Aggregate functions are not allowed in WHERE clause",
                        "function": tok
                    }

                result = consumeAggregate(tokens, i)
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

                err = validateExpression(inner, "where")
                if err:
                    return err

                expecting_operand = False
                i = end
                continue

            # Atomic operand: column or numeric literal
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
            # Expect arithmetic operator
            if tok in ARITHMETIC_OPS:
                expecting_operand = True
                i += 1
                continue

            return {
                "error": "Expected arithmetic operator",
                "position": i,
                "token": tok
            }

    # Expression cannot end while expecting an operand
    if expecting_operand:
        return {"error": "Expression cannot end with operator"}

    return None
