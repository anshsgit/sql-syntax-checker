from validator.SyntaxValidator import SyntaxValidator

class TruncateDDL:

    #TRUNCATE STATEMENT VALIDATION
    """The validateTruncateQuery method checks if a given SQL query is a valid TRUNCATE TABLE statement. 
    It performs several checks including: Required keywords (TRUNCATE TABLE), valid table name, 
    optional clauses (RESTART IDENTITY, CONTINUE IDENTITY, CASCADE, RESTRICT),"""  
    
    @staticmethod
    def validateTruncateQuery(query):
        if not query or not query.strip():
            return False, "Query is empty"

        if not SyntaxValidator.hasBalancedParentheses(query):
            return False, "Unbalanced parentheses in query"

        query = query.strip().rstrip(";")
        tokens = SyntaxValidator.tokenize(query)

        if len(tokens) < 3:
            return False, "Incomplete TRUNCATE statement"


        #KEYWORD VALIDATION
        """The method first checks that the query starts with the keywords "TRUNCATE TABLE". 
        This is essential for ensuring that the query is intended to perform a truncate operation on a table."""

        if tokens[0].upper() != "TRUNCATE":
            return False, "Statement must start with TRUNCATE"

        if tokens[1].upper() != "TABLE":
            return False, "TRUNCATE requires the TABLE keyword"

        index = 2


        #TABLE NAME VALIDATION 
        """Next, it validates the table name, which must be a valid identifier. 
        This ensures that the table being truncated is specified correctly and adheres to naming conventions."""

        if index >= len(tokens):
            return False, "Table name is missing"

        tableName = tokens[index]
        if not SyntaxValidator.isValidIdentifier(tableName):
            return False, f"Invalid table name '{tableName}'"

        index += 1


        #OPTIONS
        """After validating the table name, the method processes any optional clauses that may be present in the query. 
        It checks for the presence of RESTART IDENTITY or CONTINUE IDENTITY to determine how identity columns should be handled, 
        and CASCADE or RESTRICT to determine how referential integrity should be maintained. 
        The method ensures that these options are used correctly and that there are no conflicting or duplicate options specified."""

        identityOption = None       # RESTART / CONTINUE
        referentialOption = None    # CASCADE / RESTRICT

        while index < len(tokens):
            token = tokens[index].upper()

            #IDENTITY OPTIONS VALIDATION
            if token in ("RESTART", "CONTINUE"):
                if identityOption:
                    return False, "Duplicate identity option specified"

                if index + 1 >= len(tokens) or tokens[index + 1].upper() != "IDENTITY":
                    return False, "IDENTITY keyword must follow RESTART or CONTINUE"

                identityOption = token
                index += 2
                continue


            #REFERENTIAL OPTIONS VALIDATION
            """CASCADE and RESTRICT are mutually exclusive options that control how the TRUNCATE operation handles referential integrity constraints.
            CASCADE allows the TRUNCATE operation to proceed even if there are foreign key constraints referencing the table, 
            effectively truncating all related tables as well. RESTRICT prevents the TRUNCATE operation from proceeding,
            if there are any foreign key constraints referencing the table, ensuring that data integrity is maintained."""

            if token in ("CASCADE", "RESTRICT"):
                if referentialOption:
                    return False, "Duplicate referential option specified"

                referentialOption = token
                index += 1
                continue


            #INVALID TOKEN
            """If the method encounters any token that does not match the expected options (RESTART, CONTINUE, CASCADE, RESTRICT),
            it returns an error indicating that there is an unexpected keyword in the TRUNCATE statement."""

            return False, f"Unexpected keyword '{tokens[index]}' in TRUNCATE statement"

        return True, "Valid TRUNCATE TABLE query"
