class RollbackChecker:
    """
    Validates ROLLBACK statement syntax.
    Supports:
    - ROLLBACK;
    - ROLLBACK TO savepoint_name;
    """

    def validate(self, query: str):
        cleaned_query = query.strip().upper()

        # Simple ROLLBACK
        if cleaned_query == "ROLLBACK;":
            return {
                "valid": True,
                "message": "Valid ROLLBACK statement."
            }

        # Missing semicolon
        if cleaned_query == "ROLLBACK":
            return {
                "valid": False,
                "error": "Missing semicolon after ROLLBACK.",
                "reason": "SQL statements must end with a semicolon.",
                "suggestion": "ROLLBACK;"
            }

        # ROLLBACK TO savepoint
        if cleaned_query.startswith("ROLLBACK TO"):
            parts = cleaned_query.replace(";", "").split()

            if len(parts) == 3:
                return {
                    "valid": True,
                    "message": "Valid ROLLBACK TO SAVEPOINT statement."
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid ROLLBACK TO syntax.",
                    "reason": "ROLLBACK TO must be followed by a savepoint name.",
                    "suggestion": "ROLLBACK TO savepoint_name;"
                }

        # Missing TO keyword
        if cleaned_query.startswith("ROLLBACK ") and " TO " not in cleaned_query:
            return {
                "valid": False,
                "error": "Incorrect ROLLBACK syntax.",
                "reason": "ROLLBACK requires keyword 'TO' for savepoint rollback.",
                "suggestion": "ROLLBACK TO savepoint_name;"
            }

        return None
