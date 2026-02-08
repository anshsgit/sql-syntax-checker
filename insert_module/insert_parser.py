class InsertParser:
    def parse_insert(self, query: str) -> dict:
        parsed = {
            "raw": query,
            "table": None,
            "columns": [],
            "values": [],
            "has_into": False
        }

        if not query or not isinstance(query, str):
            return parsed

        query = query.strip().rstrip(";")
        upper_query = query.upper()

        # --- Locate VALUES keyword ---
        values_index = upper_query.find("VALUES")
        if values_index == -1:
            return parsed

        left_part = query[:values_index].strip()
        right_part = query[values_index + len("VALUES"):].strip()

        # --- Parse INSERT INTO table ---
        left_tokens = left_part.split()
        upper_tokens = [t.upper() for t in left_tokens]

        if "INTO" in upper_tokens:
            parsed["has_into"] = True
            into_index = upper_tokens.index("INTO")
            if into_index + 1 < len(left_tokens):
                parsed["table"] = left_tokens[into_index + 1]

        # --- Parse column list ---
        if "(" in left_part and ")" in left_part:
            start = left_part.find("(")
            end = left_part.find(")", start)
            column_section = left_part[start + 1:end]
            parsed["columns"] = [
                col.strip() for col in column_section.split(",") if col.strip()
            ]

        # --- Parse VALUES rows ---
        rows = []
        current = ""
        depth = 0

        for char in right_part:
            if char == "(":
                depth += 1
                current = ""
            elif char == ")":
                depth -= 1
                rows.append(current)
            elif depth > 0:
                current += char

        for row in rows:
            parsed["values"].append(
                [val.strip() for val in row.split(",")]
            )

        return parsed
