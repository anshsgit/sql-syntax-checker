from validator.SyntaxValidator import SyntaxValidator


class CreateDDL:

    # --------------------------------------------------
    # COLUMN / CONSTRAINT HELPERS
    # --------------------------------------------------

    @staticmethod
    def isTableConstraint(defn):
        first = SyntaxValidator.tokenize(defn)[0].upper()
        return first in ("PRIMARY", "UNIQUE", "FOREIGN", "CHECK")

    @staticmethod
    def validateColumnDefinition(defn):
        tokens = SyntaxValidator.tokenize(defn)

        if len(tokens) < 2:
            return {"error": "Column definition must include name and data type"}

        colName = tokens[0]
        if not SyntaxValidator.isValidIdentifier(colName):
            return {"error": f"Invalid column name '{colName}'"}

        i = 2

        while i < len(tokens):
            token = tokens[i].upper()

            if token == "PRIMARY":
                if i + 1 < len(tokens) and tokens[i + 1].upper() == "KEY":
                    i += 2
                else:
                    return {"error": "PRIMARY must be followed by KEY"}

            elif token == "UNIQUE":
                i += 1

            elif token == "NOT":
                if i + 1 < len(tokens) and tokens[i + 1].upper() == "NULL":
                    i += 2
                else:
                    return {"error": "NOT must be followed by NULL"}

            elif token == "DEFAULT":
                if i + 1 >= len(tokens):
                    return {"error": "DEFAULT must have a value"}
                i += 2

            elif token == "CHECK":
                if "(" not in defn or ")" not in defn:
                    return {"error": "CHECK constraint must be enclosed in parentheses"}
                break

            elif token == "REFERENCES":
                if i + 1 >= len(tokens):
                    return {"error": "REFERENCES must specify a table"}

                refTable = tokens[i + 1].split("(")[0]
                if not SyntaxValidator.isValidIdentifier(refTable):
                    return {"error": f"Invalid referenced table '{refTable}'"}

                if "(" not in defn or ")" not in defn:
                    return {"error": "REFERENCES must specify referenced column"}
                break

            else:
                return {"error": f"Invalid column constraint '{tokens[i]}'"}

        return None

    # --------------------------------------------------
    # CREATE TABLE
    # --------------------------------------------------

    @staticmethod
    def validateCreateTableQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        if not SyntaxValidator.hasBalancedParentheses(query):
            return {"error": "Unbalanced parentheses in query"}

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 4:
            return {"error": "Incomplete CREATE TABLE statement"}

        if tokens[0].upper() != "CREATE":
            return {"error": "Statement must start with CREATE"}

        if tokens[1].upper() != "TABLE":
            return {"error": "Expected TABLE keyword"}

        index = 2
        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return {"error": "Table name is missing"}

        tableName = tokens[index].split("(")[0]
        if not SyntaxValidator.isValidIdentifier(tableName):
            return {"error": f"Invalid table name '{tableName}'"}

        remainder = query[query.find(tableName) + len(tableName):].strip()

        if not remainder.startswith("(") or not remainder.endswith(")"):
            return {"error": "Column definitions must be enclosed in parentheses"}

        block = remainder[1:-1].strip()
        if not block:
            return {"error": "Table must have at least one column"}

        if block.endswith(","):
            return {"error": "Trailing comma in column definition is not allowed"}

        definitions = SyntaxValidator.splitByCommaRespectingParens(block)
        hasColumn = False

        for d in definitions:
            if not d:
                return {"error": "Empty column definition due to trailing comma"}

            if CreateDDL.isTableConstraint(d):
                continue

            err = CreateDDL.validateColumnDefinition(d)
            if err:
                return err

            hasColumn = True

        if not hasColumn:
            return {"error": "Table must contain at least one column"}

        return None

    # --------------------------------------------------
    # CREATE VIEW
    # --------------------------------------------------

    @staticmethod
    def validateCreateViewQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        if not SyntaxValidator.hasBalancedParentheses(query):
            return {"error": "Unbalanced parentheses in query"}

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if tokens[0].upper() != "CREATE":
            return {"error": "Statement must start with CREATE"}

        index = 1
        if tokens[index:index + 3] == ["OR", "REPLACE", "VIEW"]:
            index += 3
        elif tokens[index].upper() == "VIEW":
            index += 1
        else:
            return {"error": "Expected VIEW keyword"}

        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return {"error": "View name is missing"}

        viewName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(viewName):
            return {"error": f"Invalid view name '{viewName}'"}

        remainder = query[query.find(viewName) + len(viewName):].strip()

        if remainder.startswith("("):
            close = remainder.find(")")
            if close == -1:
                return {"error": "Unclosed column list"}

            columnBlock = remainder[1:close]
            if columnBlock.strip().endswith(","):
                return {"error": "Trailing comma in view column list is not allowed"}

            columns = SyntaxValidator.splitByCommaRespectingParens(columnBlock)
            for col in columns:
                if not col:
                    return {"error": "Empty column name in view definition"}
                if not SyntaxValidator.isValidIdentifier(col):
                    return {"error": f"Invalid view column '{col}'"}

            remainder = remainder[close + 1:].strip()

        if not remainder.upper().startswith("AS"):
            return {"error": "Missing AS keyword"}

        if not remainder[2:].strip().upper().startswith("SELECT"):
            return {"error": "CREATE VIEW must use SELECT"}

        return None

    # --------------------------------------------------
    # CREATE INDEX
    # --------------------------------------------------

    @staticmethod
    def validateCreateIndexQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 5:
            return {"error": "Incomplete CREATE INDEX statement"}

        if tokens[0].upper() != "CREATE":
            return {"error": "Statement must start with CREATE"}

        index = 1
        if tokens[index].upper() == "UNIQUE":
            index += 1

        if tokens[index].upper() != "INDEX":
            return {"error": "Expected INDEX keyword"}

        index += 1
        if index >= len(tokens):
            return {"error": "Index name is missing"}

        indexName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(indexName):
            return {"error": f"Invalid index name '{indexName}'"}

        index += 1
        if index >= len(tokens) or tokens[index].upper() != "ON":
            return {"error": "Missing ON keyword"}

        index += 1
        if index >= len(tokens):
            return {"error": "Table name is missing"}

        tableName = tokens[index].split("(")[0]
        if not SyntaxValidator.isValidIdentifier(tableName):
            return {"error": f"Invalid table name '{tableName}'"}

        onPos = query.upper().find(" ON ")
        parenStart = query.find("(", onPos)

        if parenStart == -1 or not query.endswith(")"):
            return {"error": "Index column list must be enclosed in parentheses"}

        columnBlock = query[parenStart + 1:-1].strip()
        if not columnBlock:
            return {"error": "Index must contain at least one column"}

        if columnBlock.endswith(","):
            return {"error": "Trailing comma in index column list is not allowed"}

        columns = SyntaxValidator.splitByCommaRespectingParens(columnBlock)
        for col in columns:
            parts = SyntaxValidator.tokenize(col)
            if not parts or not SyntaxValidator.isValidIdentifier(parts[0]):
                return {"error": f"Invalid index column '{parts[0]}'"}

            if len(parts) > 1 and parts[1].upper() not in ("ASC", "DESC"):
                return {"error": f"Invalid sort order '{parts[1]}'"}

        return None

    # --------------------------------------------------
    # CREATE DATABASE
    # --------------------------------------------------

    @staticmethod
    def validateCreateDatabaseQuery(query):
        if not query or not query.strip():
            return {"error": "Query is empty"}

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 3:
            return {"error": "Incomplete CREATE DATABASE statement"}

        if tokens[0].upper() != "CREATE":
            return {"error": "Statement must start with CREATE"}

        if tokens[1].upper() != "DATABASE":
            return {"error": "Expected DATABASE keyword"}

        index = 2
        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return {"error": "Database name is missing"}

        if index + 1 < len(tokens):
            return {"error": "Unexpected extra tokens after database name"}

        if not SyntaxValidator.isValidIdentifier(tokens[index]):
            return {"error": f"Invalid database name '{tokens[index]}'"}

        return None

    def validate_create(self, query):
        q = query.strip().upper()

        if q.startswith("CREATE TABLE"):
            return CreateDDL.validateCreateTableQuery(query)
        if q.startswith("CREATE VIEW"):
            return CreateDDL.validateCreateViewQuery(query)
        if q.startswith("CREATE INDEX") or q.startswith("CREATE UNIQUE INDEX"):
            return CreateDDL.validateCreateIndexQuery(query)
        if q.startswith("CREATE DATABASE"):
            return CreateDDL.validateCreateDatabaseQuery(query)

        return {"error": "Unsupported CREATE statement"}
