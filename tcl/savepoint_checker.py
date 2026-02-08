class SavepointChecker:
    """
    Validates SAVEPOINT statement syntax.
    Format:
    - SAVEPOINT savepoint_name;
    """

    def validate(self, query: str):
        cleaned_query = query.strip().upper()

        if cleaned_query.startswith("SAVEPOINT"):
            parts = cleaned_query.replace(";", "").split()

            if len(parts) == 2:
                return {
                    "valid": True,
                    "message": "Valid SAVEPOINT statement."
                }

            if cleaned_query == "SAVEPOINT;" or cleaned_query == "SAVEPOINT":
                return {
                    "valid": False,
                    "error": "Missing savepoint name.",
                    "reason": "SAVEPOINT requires a name identifier.",
                    "suggestion": "SAVEPOINT sp1;"
                }

            return {
                "valid": False,
                "error": "Invalid SAVEPOINT syntax.",
                "reason": "SAVEPOINT must be followed by exactly one name.",
                "suggestion": "SAVEPOINT sp1;"
            }

        return None
