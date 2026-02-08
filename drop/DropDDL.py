from validator.SyntaxValidator import SyntaxValidator


class DropDDL:

    #BASIC VALIDATION
    """The validateDropQuery method checks if a given SQL query is a valid DROP statement. 
    It performs several checks including: Required keywords (DROP, object type), valid object names,
    optional IF EXISTS clause, and optional CASCADE or RESTRICT clauses."""
    
    @staticmethod
    def validateDropQuery(query):

        if not query or not query.strip():
            return False, "Query is empty"

        query = query.strip().rstrip(";")
        tokens = query.split()

        if len(tokens) < 3:
            return False, "Incomplete DROP statement"

        if tokens[0].upper() != "DROP":
            return False, "Statement must start with DROP"


        #OBJECT TYPE VALIDATION
        """The method checks that the second token is one of the valid object types (TABLE, DATABASE, VIEW, INDEX). 
        This ensures that the query is intended to drop a valid type of database object and prevents invalid object types from being processed further in the validation logic."""


        objectType = tokens[1].upper()
        if objectType not in ("TABLE", "DATABASE", "VIEW", "INDEX"):
            return False, "DROP supports TABLE, DATABASE, VIEW, or INDEX only"

        index = 2


        #IF EXISTS VALIDATION
        """The method checks for the presence of the optional IF EXISTS clause, which allows the query to succeed even if the specified object does not exist. 
        If this clause is present, the method adjusts the index to skip over it and continue validating the rest of the query. 
        This ensures that the presence of IF EXISTS does not interfere with the validation of the object names and any optional CASCADE or RESTRICT clauses that may follow."""


        if (
            index + 1 < len(tokens)
            and tokens[index].upper() == "IF"
            and tokens[index + 1].upper() == "EXISTS"
        ):
            index += 2

        if index >= len(tokens):
            return False, f"Missing {objectType.lower()} name"

        remainingTokens = tokens[index:]


        #DROP DATABASE VALIDATION 
        """For DROP DATABASE, we need to ensure that only one database name is specified and that, 
        there are no trailing options like CASCADE or RESTRICT, since those options are not valid for DROP DATABASE. 
        The method checks that there is only one identifier after the DROP DATABASE keywords and that it is a valid database name."""


        if objectType == "DATABASE":
            remaining = " ".join(remainingTokens).strip()

            if ',' in remaining:
                return False, "Only one database can be dropped at a time"

            if not SyntaxValidator.isValidIdentifier(remaining):
                return False, f"Invalid database name '{remaining}'"

            return True, "Valid DROP DATABASE query"


        #CASCADE / RESTRICT VALIDATION
        """For DROP TABLE, VIEW, and INDEX, we need to validate the optional CASCADE or RESTRICT clause. 
        The method checks for the presence of these clauses at the end of the query and ensures that they are not duplicated or used incorrectly. 
        It also ensures that there is at least one object name specified before the CASCADE or RESTRICT clause if it is present."""


        options = [t.upper() for t in remainingTokens if t.upper() in ("CASCADE", "RESTRICT")]
        if len(options) > 1:
            return False, "Only one of CASCADE or RESTRICT is allowed"

        cascadeOption = None
        lastToken = remainingTokens[-1].upper()

        if lastToken in ("CASCADE", "RESTRICT"):
            cascadeOption = lastToken
            remainingTokens = remainingTokens[:-1]

            if not remainingTokens:
                return False, f"{cascadeOption} must follow at least one {objectType.lower()} name"
            

        #OBJECT NAME VALIDATION
        """Finally, the method validates the list of object names specified in the query. 
        It ensures that each name is a valid identifier and that there are no empty names or trailing commas."""


        remaining = " ".join(remainingTokens).strip()

        if remaining.endswith(','):
            return False, "Trailing comma is not allowed"

        rawNames = remaining.split(',')
        names = []

        for name in rawNames:
            stripped = name.strip()
            if not stripped:
                return False, "Empty object name between commas is not allowed"
            names.append(stripped)

        if not names:
            return False, f"No {objectType.lower()} names specified"

        for name in names:
            if not SyntaxValidator.isValidIdentifier(name):
                return False, f"Invalid {objectType.lower()} name '{name}'"

        return True, f"Valid DROP {objectType} query ({len(names)} item(s))"
