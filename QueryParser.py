from select_module.selectParser import SelectParser
from Alter_module.alter import AlterCommand
from Delete_module.delete import DeleteCommand
from insert_module.insert_command import InsertCommand
from update_module.update import UpdateCommand
from create.CreateDDL import CreateDDL
from truncate.TruncateDDL import TruncateDDL
from drop.DropDDL import DropDDL
from tcl.tcl_validator import TCLValidator
from select_module.helper.utils import spell_check_tokens

class QueryParser:
    """
    Top-level SQL query parser and dispatcher.

    Responsibilities:
    - Tokenize raw SQL input
    - Validate query-level syntax (semicolon, empty query)
    - Route query to the appropriate statement parser
    """

    def __init__(self, query):
        self.query = query

        # Supported SQL statement types
        self.queryTypes = [
            'select', 'insert', 'update',
            'alter', 'drop', 'delete',
            'truncate', 'create', 'commit', 'rollback', 'savepoint'
        ]

        # Comparison operators (used by tokenization / validation)
        self.comparators = {"=", "!=", "<", ">", "<=", ">="}

    # ---------------------------------------------------------
    # Tokenization
    # ---------------------------------------------------------

    def tokenize(self):
        """
        Converts raw SQL string into a list of tokens.

        Rules:
        - Identifiers are lowercased
        - Operators are grouped (<=, >=, !=)
        - Symbols are emitted as standalone tokens
        - Whitespace is ignored
        """
        sql = self.query.strip()
        tokens = []
        word = ""
        i = 0

        OP_CHARS = set("<>!=")

        while i < len(sql):
            ch = sql[i]

            # Build identifiers (letters, digits, underscore)
            if ch.isalnum() or ch == "_":
                word += ch
                i += 1
                continue

            # Flush accumulated identifier
            if word:
                tokens.append(word.lower())
                word = ""

            # Operator token (possibly multi-character)
            if ch in OP_CHARS:
                op = ch
                i += 1
                while i < len(sql) and sql[i] in OP_CHARS:
                    op += sql[i]
                    i += 1
                tokens.append(op)
                continue

            # Single-character tokens
            if ch in {",", "(", ")", ";", "*", "+", "-", "/", "%", "."}:
                tokens.append(ch)
                i += 1
                continue

            # Ignore whitespace and unknown characters
            i += 1

        # Flush trailing identifier
        if word:
            tokens.append(word.lower())

        return tokens

    def analyse(self):
        """
        Main entry point for query validation.
        Performs:
        - Tokenization
        - Semicolon validation
        - Query type detection
        - Delegation to statement-specific parser
        """
        tokens = self.tokenize()

        # Empty input
        if not tokens:
            return {
                "error": "empty query"
            }
        
        # spell_errors = spell_check_tokens(tokens)
        # print(spell_errors)
        # suggestion = spell_errors[0]['suggestions'][0]

        # if spell_errors:
        #     return {
        #         "error": f"Spelling mistake in SQL keyword. Do you mean {suggestion}",
        #     }


        # Semicolon validation
        if ";" in tokens:
            if tokens[-1] != ";":
                return {
                    "error": "Invalid semicolon usage",
                    "why": "semicolon is only allowed at the end of the query"
                }

            # Remove trailing semicolon
            tokens = tokens[:-1]

            # Reject multiple semicolons
            if tokens and tokens[-1] == ";":
                return {
                    "error": "Multiple semicolon not allowed"
                }

        if not tokens:
            return {"empty query"}

        # Determine query type
        queryType = tokens[0]
        print(queryType)

        if queryType not in self.queryTypes:
            return {
                "Error": "Invalid sql query",
                "Issue": "The start token is not a valid sql keyword"
            }

        if queryType == "alter":
            parser = AlterCommand(self.query)
            return parser.analyse()
        elif queryType == "delete":
            parser = DeleteCommand(self.query)
            return parser.validate()
        elif queryType == "insert":
            parser = InsertCommand()
            return parser.validate(self.query)
        elif queryType == "update":
            parser = UpdateCommand(self.query)
            return parser.validate()
        elif queryType == "create":
            parser = CreateDDL()
            return parser.validate_create(self.query)
        elif queryType == 'truncate':
            return TruncateDDL.validateTruncateQuery(self.query)
        elif queryType == 'drop':
            return DropDDL.validateDropQuery(self.query)
        elif queryType in ("commit", "rollback", "savepoint"):
            parser = TCLValidator()
            return parser.validate(self.query)
        elif queryType == "select":
            parser = SelectParser()
            return parser.analyse(tokens)
        else:
            return {
                "error": "Not a valid query or query not supported"
            }
