class CommitChecker:
    """
    Validates COMMIT statement syntax.
    COMMIT must be a standalone statement with no arguments.
    """

    def validate(self, query: str):
        cleaned_query = query.strip().upper()

        # Correct COMMIT
        if cleaned_query == "COMMIT;":
            return {
                "valid": True,
                "message": "Valid COMMIT statement."
            }

        # COMMIT without semicolon
        if cleaned_query == "COMMIT":
            return {
                "valid": False,
                "error": "Missing semicolon after COMMIT.",
                "reason": "SQL statements must end with a semicolon.",
                "suggestion": "COMMIT;"
            }

        # COMMIT with extra words
        if cleaned_query.startswith("COMMIT"):
            return {
                "valid": False,
                "error": "Invalid COMMIT usage.",
                "reason": "COMMIT must be used as a standalone statement.",
                "suggestion": "COMMIT;"
            }

        return None
