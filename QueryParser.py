from select.selectParser import SelectParser

class QueryParser:

    def __init__(self, query):
        self.query = query
        self.queryTypes = ['select', 'insert', 'update', 'alter', 'drop', 'delete', 'truncate', 'create']
        self.comparators  = {"=", "!=", "<", ">", "<=", ">="}

    def tokenize(self):
        sql = self.query.strip()
        tokens = []
        word = ""
        i = 0

        OP_CHARS = set("<>!=")

        while i < len(sql):
            ch = sql[i]

            if ch.isalnum() or ch == "_":
                word += ch
                i += 1
                continue

            if word:
                tokens.append(word.lower())
                word = ""

            if ch in OP_CHARS:
                op = ch
                i += 1
                while i < len(sql) and sql[i] in OP_CHARS:
                    op += sql[i]
                    i += 1
                tokens.append(op)
                continue

            if ch in {",", "(", ")", ";", "*", '+', '-', '/', '%', '.'}:
                tokens.append(ch)
                i += 1
                continue

            i += 1

        if word:
            tokens.append(word.lower())

        # print(tokens)

        return tokens


    def route(self, token):

        match token:
            case "select":
                return SelectParser()
            case "alter":
                pass
            case "create":
                pass
            case "update":
                pass
            case "drop":
                pass
            case "delete":
                pass
            case "truncate":
                pass
            case "insert":
                pass

    def analyse(self):
        
        tokens = self.tokenize()

        if not tokens:
            return {
                "error": "empty query"
            }
        
        if ";" in tokens:
            if tokens[-1] != ";":
                return {
                    "error": "Invalid semicolon usage",
                    "why": "semicolon is only allowed at the end of the query"
                }
            
            tokens = tokens[:-1]
            if tokens and tokens[:-1]:
                return {
                    "error": "Multiple semicolon not allowed"
                }
            
        if not tokens:
            return {"empty query"}

        queryType = tokens[0]

        if queryType not in self.queryTypes:
            return {
                "Error": "Invalid sql query",
                "Issue": "The start token is not a valid sql keyword"
            }

        parser = self.route(queryType)
        return parser.analyse(tokens)
