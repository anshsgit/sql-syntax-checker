class InsertValidator:
    def validate_insert(self, parsed: dict):
        raw_query = parsed.get("raw")

        if not raw_query or not isinstance(raw_query, str):
            return {
                "error": "Empty or invalid query.",
                "suggestion": "Provide a valid INSERT statement."
            }

        upper_query = raw_query.upper()

        if not upper_query.strip().startswith("INSERT"):
            return {
                "error": "Query does not start with INSERT.",
                "suggestion": "INSERT statements must begin with INSERT."
            }

        if "INTO" not in upper_query:
            return {
                "error": "Missing INTO keyword.",
                "suggestion": "Use: INSERT INTO <table> VALUES (...)"
            }

        if parsed.get("has_into") and not parsed.get("table"):
            return {
                "error": "Missing table name.",
                "suggestion": "Specify a table name after INTO."
            }

        if "VALUES" not in upper_query:
            return {
                "error": "Missing VALUES clause.",
                "suggestion": "INSERT requires a VALUES clause."
            }

        values = parsed.get("values", [])
        if not values:
            return {
                "error": "VALUES clause is incorrectly formatted.",
                "suggestion": "VALUES must contain at least one value list."
            }

        columns = parsed.get("columns", [])
        if columns:
            col_count = len(columns)
            for row in values:
                if len(row) != col_count:
                    return {
                        "error": "Column-value count mismatch.",
                        "suggestion": (
                            f"{col_count} columns specified but "
                            f"{len(row)} values provided."
                        )
                    }

        for row in values:
            if not any(val for val in row):
                return {
                    "error": "Empty VALUES list.",
                    "suggestion": "VALUES cannot be empty."
                }

        return None
