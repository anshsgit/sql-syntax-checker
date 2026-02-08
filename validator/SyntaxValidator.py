class SyntaxValidator:

    #IDENTIFIER VALIDATION

    #isQuotedIdentifier
    """The isQuotedIdentifier method checks if the name is a quoted identifier, 
    which starts and ends with double quotes."""  
    @staticmethod
    def isQuotedIdentifier(name):
        return name.startswith('"') and name.endswith('"')
    

    #isSimpleIdentifier
    """The isSimpleIdentifier method checks if the name is a simple identifier, 
    which must start with a letter or underscore and can only contain letters, digits, or underscores."""
    @staticmethod
    def isSimpleIdentifier(name):
        if not name:
            return False

        if not (name[0].isalpha() or name[0] == '_'):
            return False

        for ch in name:
            if not (ch.isalnum() or ch == '_'):
                return False

        return True


    #isValidIdentifier
    """The isValidIdentifier method combines these checks to determine if a name is a valid identifier, 
    allowing for both quoted and simple identifiers, as well as dot notation for schema-qualified names."""
    @staticmethod
    def isValidIdentifier(name):
        name = name.strip()

        if SyntaxValidator.isQuotedIdentifier(name):
            return bool(name[1:-1].strip())

        if '.' in name:
            parts = name.split('.')
            if len(parts) != 2:
                return False
            return all(SyntaxValidator.isSimpleIdentifier(p) for p in parts)

        return SyntaxValidator.isSimpleIdentifier(name)


    #LIST / COMMA HELPERS 

    #tokenize
    """The tokenize method splits a SQL query into tokens while respecting quoted identifiers,
    i.e. "users name" should be treated as a single token, 
    ensuring that spaces within quotes do not break the tokenization."""
    @staticmethod
    def tokenize(name):
    
        tokens = []
        current = ""
        in_quote = False
        quote_char = ""

        for ch in name:
            if ch in ('"', '`'):
                if in_quote and ch == quote_char:
                    in_quote = False
                elif not in_quote:
                    in_quote = True
                    quote_char = ch

            if ch.isspace() and not in_quote:
                if current:
                    tokens.append(current)
                    current = ""
            else:
                current += ch

        if current:
            tokens.append(current)

        return tokens


    #hasBalancedParentheses
    """The hasBalancedParentheses method checks if the parentheses in the query are balanced, 
    ensuring that every opening parenthesis has a corresponding closing parenthesis and that they are properly nested."""
    @staticmethod
    def hasBalancedParentheses(name):
        depth = 0
        in_quote = False

        for ch in name:
            if ch in ('"', '`'):
                in_quote = not in_quote

            if in_quote:
                continue

            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth < 0:
                    return False

        return depth == 0
    

    #splitSimpleComma
    """The splitSimpleComma method splits a string by commas and trims whitespace from each part, 
    returning a list of non-empty parts. This is useful for parsing lists of identifiers or values in SQL queries."""
    @staticmethod
    def splitSimpleComma(text):
        return [p.strip() for p in text.split(',') if p.strip()]

    @staticmethod
    def splitByCommaRespectingParens(text):
        tokens = []
        current = ""
        depth = 0

        for ch in text:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1

            if ch == ',' and depth == 0:
                tokens.append(current.strip())
                current = ""
            else:
                current += ch

        if current.strip():
            tokens.append(current.strip())

        return tokens

    #BASIC KEYWORD CHECK 

    #startsWithKeyword
    """The startsWithKeyword method checks if the query starts with a specific keyword, 
    ignoring leading whitespace and case sensitivity. 
    This is a basic check to quickly validate the type of SQL statement being processed."""
    @staticmethod
    def startsWithKeyword(query, keyword):
        return query.strip().upper().startswith(keyword)
