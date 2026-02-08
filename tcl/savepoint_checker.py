class SavepointChecker:
    def validate(self, query: str):
        if not query or not query.strip():
            return None

        cleaned = query.strip().upper()

        if not cleaned.startswith("SAVEPOINT"):
            return None  # not my statement

        tokens = cleaned.rstrip(";").split()

        if cleaned in ("SAVEPOINT", "SAVEPOINT;"):
            return {
                "error": "Missing savepoint name.",
                "suggestion": "SAVEPOINT sp1;"
            }

        if len(tokens) != 2:
            return {
                "error": "Invalid SAVEPOINT syntax.",
                "suggestion": "SAVEPOINT sp1;"
            }

        return None  # ✅ valid
