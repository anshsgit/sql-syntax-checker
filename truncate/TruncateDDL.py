from validator.SyntaxValidator import SyntaxValidator


class TruncateDDL:

    @staticmethod
    def validateTruncateQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        if not SyntaxValidator.hasBalancedParentheses(query):
            return {"error": "Unbalanced parentheses in query"}

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 3:
            return {"error": "Incomplete TRUNCATE statement"}

        # ---- keyword validation ----
        if tokens[0].upper() != "TRUNCATE":
            return {"error": "Statement must start with TRUNCATE"}

        if tokens[1].upper() != "TABLE":
            return {"error": "TRUNCATE requires the TABLE keyword"}

        index = 2

        # ---- table name ----
        if index >= len(tokens):
            return {"error": "Table name is missing"}

        tableName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(tableName):
            return {"error": f"Invalid table name '{tableName}'"}

        index += 1

        # ---- options ----
        identityOption = None       # RESTART / CONTINUE
        referentialOption = None    # CASCADE / RESTRICT

        while index < len(tokens):
            token = tokens[index].upper()

            # RESTART / CONTINUE IDENTITY
            if token in ("RESTART", "CONTINUE"):
                if identityOption:
                    return {"error": "Duplicate identity option specified"}

                if index + 1 >= len(tokens) or tokens[index + 1].upper() != "IDENTITY":
                    return {"error": "IDENTITY keyword must follow RESTART or CONTINUE"}

                identityOption = token
                index += 2
                continue

            # CASCADE / RESTRICT
            if token in ("CASCADE", "RESTRICT"):
                if referentialOption:
                    return {"error": "Duplicate referential option specified"}

                referentialOption = token
                index += 1
                continue

            return {
                "error": f"Unexpected keyword '{tokens[index]}' in TRUNCATE statement"
            }

        return None
