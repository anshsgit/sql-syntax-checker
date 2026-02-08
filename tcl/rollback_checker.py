class RollbackChecker:
    def validate(self, query: str):
        if not query or not query.strip():
            return None

        cleaned = query.strip().upper()

        if not cleaned.startswith("ROLLBACK"):
            return None  # not my statement

        if cleaned == "ROLLBACK":
            return {
                "error": "Missing semicolon after ROLLBACK.",
                "suggestion": "ROLLBACK;"
            }

        if cleaned == "ROLLBACK;":
            return None

        if cleaned.startswith("ROLLBACK TO"):
            tokens = cleaned.rstrip(";").split()
            if len(tokens) == 3:
                return None

            return {
                "error": "Invalid ROLLBACK TO syntax.",
                "suggestion": "ROLLBACK TO savepoint_name;"
            }

        return {
            "error": "Incorrect ROLLBACK syntax.",
            "suggestion": "ROLLBACK; or ROLLBACK TO savepoint_name;"
        }
