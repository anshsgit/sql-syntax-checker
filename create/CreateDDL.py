from validator.SyntaxValidator import SyntaxValidator

class CreateDDL:

    #COLUMN / CONSTRAINT VALIDATION 

    #isTableConstraint
    """The isTableConstraint method checks if a given definition is a table-level constraint by looking at,
    the first token and determining if it matches known constraint types such as PRIMARY, UNIQUE, FOREIGN, or CHECK."""

    @staticmethod
    def isTableConstraint(defn):
        first = SyntaxValidator.tokenize(defn)[0].upper()
        return first in ("PRIMARY", "UNIQUE", "FOREIGN", "CHECK")


    @staticmethod
    def validateColumnDefinition(defn):
        tokens = SyntaxValidator.tokenize(defn)

        # Column name + data type required
        if len(tokens) < 2:
            return False, "Column definition must include name and data type"

        colName = tokens[0]
        if not SyntaxValidator.isValidIdentifier(colName):
            return False, f"Invalid column name '{colName}'"

        i = 2  # start after column name and data type

        while i < len(tokens):
            token = tokens[i].upper()

            # PRIMARY KEY
            if token == "PRIMARY":
                if i + 1 < len(tokens) and tokens[i + 1].upper() == "KEY":
                    i += 2
                else:
                    return False, "PRIMARY must be followed by KEY"

            # UNIQUE
            elif token == "UNIQUE":
                i += 1

            # NOT NULL
            elif token == "NOT":
                if i + 1 < len(tokens) and tokens[i + 1].upper() == "NULL":
                    i += 2
                else:
                    return False, "NOT must be followed by NULL"

            # DEFAULT value
            elif token == "DEFAULT":
                if i + 1 >= len(tokens):
                    return False, "DEFAULT must have a value"
                i += 2

            # CHECK (...)
            elif token == "CHECK":
                if "(" not in defn or ")" not in defn:
                    return False, "CHECK constraint must be enclosed in parentheses"
                break  # do not parse inside CHECK

            # REFERENCES table(column)
            elif token == "REFERENCES":
                if i + 1 >= len(tokens):
                    return False, "REFERENCES must specify a table"
                refToken = tokens[i + 1]
                refTable = refToken.split("(")[0]

                if not SyntaxValidator.isValidIdentifier(refTable):
                    return False, f"Invalid referenced table '{refTable}'"
            
                if "(" not in defn or ")" not in defn:
                    return False, "REFERENCES must specify referenced column"
                break  # do not parse inside REFERENCES

            else:
                return False, f"Invalid column constraint '{tokens[i]}'"

        return True, ""


    #CREATE TABLE VALIDATION

    #validateCreateTableQuery
    """The validateCreateTableQuery method validates a CREATE TABLE SQL query by checking for correct syntax,
    ensuring that the query starts with CREATE TABLE (optionally with IF NOT EXISTS), validating the table name as a proper identifier, 
    checking that column definitions are enclosed in parentheses, ensuring that there is at least one column defined, 
    and validating each column definition for proper structure and constraints."""

    @staticmethod
    def validateCreateTableQuery(query):
        if not query or not query.strip():
            return False, "Query is empty"

        if not SyntaxValidator.hasBalancedParentheses(query):
            return False, "Unbalanced parentheses in query"

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 4:
            return False, "Incomplete CREATE TABLE statement"

        if tokens[0].upper() != "CREATE":
            return False, "Statement must start with CREATE"

        if tokens[1].upper() != "TABLE":
            return False, "Expected TABLE keyword"

        index = 2
        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return False, "Table name is missing"

        tableToken = tokens[index]
        tableName = tableToken.split("(")[0]

        if not SyntaxValidator.isValidIdentifier(tableName):
            return False, f"Invalid table name '{tableName}'"

        remainder = query[query.find(tableName) + len(tableName):].strip()

        if not remainder.startswith("(") or not remainder.endswith(")"):
            return False, "Column definitions must be enclosed in parentheses"

        block = remainder[1:-1].strip()

        if not block:
            return False, "Table must have at least one column"

        if block.endswith(","):
            return False, "Trailing comma in column definition is not allowed"

        definitions = SyntaxValidator.splitByCommaRespectingParens(block)
        hasColumn = False

        for d in definitions:
            if not d:
                return False, "Empty column definition due to trailing comma"

            #TABLE-LEVEL CONSTRAINTS
            if CreateDDL.isTableConstraint(d):
                continue

            #COLUMN-LEVEL VALIDATION 
            valid, msg = CreateDDL.validateColumnDefinition(d)
            if not valid:
                return False, msg

            hasColumn = True

        if not hasColumn:
            return False, "Table must contain at least one column"

        return True, "Valid CREATE TABLE query"


    #CREATE VIEW VALIDATION

    #validateCreateViewQuery
    """The validateCreateViewQuery method validates a CREATE VIEW SQL query by checking for correct syntax,
    ensuring that the query starts with CREATE VIEW (optionally with OR REPLACE and IF NOT EXISTS), validating the view name as a proper identifier, 
    checking for an optional column list, and confirming that the query contains a valid SELECT statement following the AS keyword."""
   
    @staticmethod
    def validateCreateViewQuery(query):
        if not query or not query.strip():
            return False, "Query is empty"

        if not SyntaxValidator.hasBalancedParentheses(query):
            return False, "Unbalanced parentheses in query"

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if tokens[0].upper() != "CREATE":
            return False, "Statement must start with CREATE"

        index = 1
        if tokens[index:index + 3] == ["OR", "REPLACE", "VIEW"]:
            index += 3
        elif tokens[index].upper() == "VIEW":
            index += 1
        else:
            return False, "Expected VIEW keyword"

        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return False, "View name is missing"

        viewName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(viewName):
            return False, f"Invalid view name '{viewName}'"

        remainder = query[query.find(viewName) + len(viewName):].strip()

        if remainder.startswith("("):
            close = remainder.find(")")
            if close == -1:
                return False, "Unclosed column list"

            columnBlock = remainder[1:close]

            if columnBlock.strip().endswith(","):
                return False, "Trailing comma in view column list is not allowed"

            columns = SyntaxValidator.splitByCommaRespectingParens(columnBlock)
            for col in columns:
                if not col:
                    return False, "Empty column name in view definition"
                if not SyntaxValidator.isValidIdentifier(col):
                    return False, f"Invalid view column '{col}'"

            remainder = remainder[close + 1:].strip()

        if not remainder.upper().startswith("AS"):
            return False, "Missing AS keyword"

        selectPart = remainder[2:].strip()
        if not selectPart.upper().startswith("SELECT"):
            return False, "CREATE VIEW must use SELECT"

        return True, "Valid CREATE VIEW query"


    #CREATE INDEX VALIDATION 

    #validateCreateIndexQuery
    """The validateCreateIndexQuery method validates a CREATE INDEX SQL query by checking for correct syntax, 
    ensuring that the query starts with CREATE INDEX (optionally with UNIQUE), validating the index name and table name as proper identifiers, 
    confirming the presence of the ON keyword, and verifying that the index column list is properly enclosed in parentheses,
    and contains valid column names without trailing commas."""

    @staticmethod
    def validateCreateIndexQuery(query):
        if not query or not query.strip():
            return False, "Query is empty"

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 5:
            return False, "Incomplete CREATE INDEX statement"

        if tokens[0].upper() != "CREATE":
            return False, "Statement must start with CREATE"

        index = 1

        # UNIQUE (optional)
        if tokens[index].upper() == "UNIQUE":
            index += 1
            if index >= len(tokens):
                return False, "INDEX keyword is missing"

        # INDEX keyword
        if tokens[index].upper() != "INDEX":
            return False, "Expected INDEX keyword"

        index += 1
        if index >= len(tokens):
            return False, "Index name is missing"

        # Index name
        indexName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(indexName):
            return False, f"Invalid index name '{indexName}'"

        index += 1
        if index >= len(tokens) or tokens[index].upper() != "ON":
            return False, "Missing ON keyword"

        index += 1
        if index >= len(tokens):
            return False, "Table name is missing"

        # Table name
        tableToken = tokens[index]
        tableName = tableToken.split("(")[0]

        if not SyntaxValidator.isValidIdentifier(tableName):
            return False, f"Invalid table name '{tableName}'"

        onPos = query.upper().find(" ON ")
        parenStart = query.find("(", onPos)

        if parenStart == -1 or not query.endswith(")"):
            return False, "Index column list must be enclosed in parentheses"

        columnBlock = query[parenStart + 1:-1].strip()

        if not columnBlock:
            return False, "Index must contain at least one column"

        if columnBlock.endswith(","):
            return False, "Trailing comma in index column list is not allowed"

        columns = SyntaxValidator.splitByCommaRespectingParens(columnBlock)

        for col in columns:
            parts = SyntaxValidator.tokenize(col)
            if not parts:
                return False, "Empty index column definition"

            if not SyntaxValidator.isValidIdentifier(parts[0]):
                return False, f"Invalid index column '{parts[0]}'"

            if len(parts) > 1:
                order = parts[1].upper()
                if order not in ("ASC", "DESC"):
                    return False, f"Invalid sort order '{parts[1]}'"

        return True, "Valid CREATE INDEX query"


    #CREATE DATABASE VALIDATION 

    #validateCreateDatabaseQuery
    """The validateCreateDatabaseQuery method validates a CREATE DATABASE SQL query by checking for correct syntax, 
    ensuring that the query starts with CREATE DATABASE (optionally with IF NOT EXISTS), validating the database name as a proper identifier,
    and confirming that there are no unexpected extra tokens after the database name."""

    @staticmethod
    def validateCreateDatabaseQuery(query):
        if not query or not query.strip():
            return False, "Query is empty"

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 3:
            return False, "Incomplete CREATE DATABASE statement"

        if tokens[0].upper() != "CREATE":
            return False, "Statement must start with CREATE"

        if tokens[1].upper() != "DATABASE":
            return False, "Expected DATABASE keyword"

        index = 2
        if tokens[index:index + 3] == ["IF", "NOT", "EXISTS"]:
            index += 3

        if index >= len(tokens):
            return False, "Database name is missing"

        if index + 1 < len(tokens):
            return False, "Unexpected extra tokens after database name"

        dbName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(dbName):
            return False, f"Invalid database name '{dbName}'"

        return True, "Valid CREATE DATABASE query"
