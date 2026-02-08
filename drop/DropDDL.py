from validator.SyntaxValidator import SyntaxValidator


class DropDDL:

    @staticmethod
    def validateDropQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        query = query.strip().rstrip(";")
        tokens = query.split()

        if len(tokens) < 3:
            return {"error": "Incomplete DROP statement"}

        if tokens[0].upper() != "DROP":
            return {"error": "Statement must start with DROP"}

        # ---- object type ----
        objectType = tokens[1].upper()
        if objectType not in ("TABLE", "DATABASE", "VIEW", "INDEX"):
            return {
                "error": "DROP supports TABLE, DATABASE, VIEW, or INDEX only"
            }

        index = 2

        # ---- IF EXISTS ----
        if (
            index + 1 < len(tokens)
            and tokens[index].upper() == "IF"
            and tokens[index + 1].upper() == "EXISTS"
        ):
            index += 2

        if index >= len(tokens):
            return {
                "error": f"Missing {objectType.lower()} name"
            }

        remainingTokens = tokens[index:]

        # --------------------------------------------------
        # DROP DATABASE (special case)
        # --------------------------------------------------
        if objectType == "DATABASE":
            remaining = " ".join(remainingTokens).strip()

            if "," in remaining:
                return {
                    "error": "Only one database can be dropped at a time"
                }

            if not SyntaxValidator.isValidIdentifier(remaining):
                return {
                    "error": f"Invalid database name '{remaining}'"
                }

            return None

        # --------------------------------------------------
        # CASCADE / RESTRICT
        # --------------------------------------------------
        options = [
            t.upper() for t in remainingTokens
            if t.upper() in ("CASCADE", "RESTRICT")
        ]

        if len(options) > 1:
            return {
                "error": "Only one of CASCADE or RESTRICT is allowed"
            }

        lastToken = remainingTokens[-1].upper()
        if lastToken in ("CASCADE", "RESTRICT"):
            remainingTokens = remainingTokens[:-1]
            if not remainingTokens:
                return {
                    "error": f"{lastToken} must follow at least one {objectType.lower()} name"
                }

        # --------------------------------------------------
        # object names
        # --------------------------------------------------
        remaining = " ".join(remainingTokens).strip()

        if remaining.endswith(","):
            return {
                "error": "Trailing comma is not allowed"
            }

        rawNames = remaining.split(",")
        names = []

        for name in rawNames:
            stripped = name.strip()
            if not stripped:
                return {
                    "error": "Empty object name between commas is not allowed"
                }
            names.append(stripped)

        if not names:
            return {
                "error": f"No {objectType.lower()} names specified"
            }

        for name in names:
            if not SyntaxValidator.isValidIdentifier(name):
                return {
                    "error": f"Invalid {objectType.lower()} name '{name}'"
                }

        return None
