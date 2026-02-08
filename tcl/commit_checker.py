class CommitChecker:
    def validate(self, query: str):
        if not query or not query.strip():
            return None

        cleaned = query.strip().upper()

        if not cleaned.startswith("COMMIT"):
            return None  # not my statement

        if cleaned == "COMMIT":
            return {
                "error": "Missing semicolon after COMMIT.",
                "suggestion": "COMMIT;"
            }

        if cleaned == "COMMIT;":
            return None

        return {
            "error": "Invalid COMMIT usage.",
            "suggestion": "COMMIT;"
        }
