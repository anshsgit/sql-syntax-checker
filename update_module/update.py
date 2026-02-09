from select_module.helper.whereChecksHelper import (
    extractConditions,
    checkParentheses,
    validateBooleanExpr
)


class UpdateCommand:
    def __init__(self, query: str):
        self.query = query.strip() if isinstance(query, str) else ""

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _is_identifier(self, token):
        if not token:
            return False
        if token.upper() in {"UPDATE", "SET", "WHERE"}:
            return False
        if not token[0].isalpha():
            return False
        return all(ch.isalnum() or ch == "_" for ch in token)

    def _tokenize(self):
        sql = self.query
        tokens = []
        word = ""
        i = 0

        while i < len(sql):
            ch = sql[i]

            # string literal
            if ch == "'":
                literal = "'"
                i += 1
                while i < len(sql) and sql[i] != "'":
                    literal += sql[i]
                    i += 1
                if i >= len(sql):
                    return None  # unterminated string
                literal += "'"
                tokens.append(literal)
                i += 1
                continue

            if ch.isalnum() or ch == "_":
                word += ch
            else:
                if word:
                    tokens.append(word.upper())
                    word = ""
                # ⬇️ ignore semicolons completely
                if ch.strip() and ch != ";":
                    tokens.append(ch)

            i += 1

        if word:
            tokens.append(word.upper())

        return tokens


    # --------------------------------------------------
    # Validator
    # --------------------------------------------------
    def validate(self):
        # ---- empty query ----
        if not self.query:
            return {
                "error": "Empty query.",
                "suggestion": "Provide an UPDATE statement."
            }

        tokens = self._tokenize()
        if tokens is None:
            return {
                "error": "Unterminated string literal.",
                "suggestion": "Close all string literals with a single quote."
            }

        # ---- UPDATE keyword ----
        if tokens.count("UPDATE") != 1:
            return {
                "error": "UPDATE must appear exactly once.",
                "suggestion": None
            }

        if "SET" not in tokens:
            return {
                "error": "Missing SET clause.",
                "suggestion": "UPDATE requires a SET clause."
            }

        if tokens.count("SET") != 1:
            return {
                "error": "SET clause appears more than once.",
                "suggestion": None
            }

        update_idx = tokens.index("UPDATE")
        set_idx = tokens.index("SET")
        where_idx = tokens.index("WHERE") if "WHERE" in tokens else None

        if set_idx < update_idx:
            return {
                "error": "SET clause appears before UPDATE.",
                "suggestion": "Correct order is UPDATE → SET → WHERE."
            }

        if where_idx is not None and where_idx < set_idx:
            return {
                "error": "WHERE clause appears before SET.",
                "suggestion": "Correct order is UPDATE → SET → WHERE."
            }

        table_idx = update_idx + 1
        if table_idx >= len(tokens) or not self._is_identifier(tokens[table_idx]):
            return {
                "error": "Invalid or missing table name"
            }

        # NEXT TOKEN MUST BE SET (not another table)
        next_idx = table_idx + 1
        if next_idx >= len(tokens) or tokens[next_idx].lower() != "set":
            return {
                "error": "UPDATE supports only one table",
                "suggestion": "Use UPDATE <table> SET column = value"
            }
        # --------------------------------------------------
        # SET clause validation (multiple assignments)
        # --------------------------------------------------
        set_start = set_idx + 1
        set_end = where_idx if where_idx is not None else len(tokens)
        set_tokens = tokens[set_start:set_end]

        if not set_tokens:
            return {
                "error": "Empty SET clause.",
                "suggestion": "Specify at least one column assignment."
            }

        i = 0
        expecting_assignment = True

        while i < len(set_tokens):
            if expecting_assignment:
                if (
                    i + 2 >= len(set_tokens)
                    or not self._is_identifier(set_tokens[i])
                    or set_tokens[i + 1] != "="
                ):
                    return {
                        "error": "Invalid SET assignment.",
                        "suggestion": "Use: column = value [, column = value]"
                    }
                i += 3
                expecting_assignment = False
            else:
                if set_tokens[i] != ",":
                    return {
                        "error": "Missing comma between SET assignments.",
                        "suggestion": "Separate assignments with commas."
                    }
                i += 1
                expecting_assignment = True

        if expecting_assignment:
            return {
                "error": "Trailing comma in SET clause.",
                "suggestion": "Remove the trailing comma."
            }

        # --------------------------------------------------
        # WHERE clause (REUSED from SELECT module)
        # --------------------------------------------------
        if where_idx is not None:
            # WHERE engine expects lowercase tokens
            lower_tokens = [t.lower() if isinstance(t, str) else t for t in tokens]

            where_tokens = extractConditions(lower_tokens)
            if not where_tokens:
                return {
                    "error": "Empty WHERE clause.",
                    "suggestion": "Specify a condition after WHERE."
                }

            err = checkParentheses(where_tokens)
            if err:
                return err

            err = validateBooleanExpr(where_tokens, clause="where")
            if err:
                return err

        # ---- valid ----
        return None
