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

            if ch in {",", "(", ")", ";", "*", '+', '-', '/', '%'}:
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
        
        queryType = tokens[0]

        if queryType not in self.queryTypes:
            return {
                "Error": "Invalid sql query",
                "Issue": "The start token is not a valid sql keyword"
            }

        parser = self.route(queryType)
        return parser.analyse(tokens)




TEST_CASES = [
    # ---------- SELECT clause violations ----------
    ("SELECT a,, b FROM t WHERE a = 1", False),          # double comma
    ("SELECT a , , b FROM t WHERE a = 1", False),        # spaced double comma
    ("SELECT a b c FROM t WHERE a = 1", False),          # multiple missing commas
    ("SELECT * a FROM t WHERE a = 1", False),            # * mixed without comma
    ("SELECT count FROM t WHERE a = 1", False),          # aggregate without ()
    ("SELECT sum() FROM t WHERE a = 1", False),          # empty aggregate args
    ("SELECT sum(a,) FROM t WHERE a = 1", False),        # trailing comma in aggregate
    ("SELECT a AS 123 FROM t WHERE a = 1", False),       # numeric alias
    ("SELECT a AS select FROM t WHERE a = 1", False),    # keyword alias
    ("SELECT a AS b c FROM t WHERE a = 1", False),       # alias without AS support
    ("SELECT a AS FROM FROM t WHERE a = 1", False),      # double keyword misuse

    # ---------- FROM clause issues ----------
    ("SELECT a WHERE a = 1", False),                     # missing FROM
    ("SELECT a FROM WHERE a = 1", False),                # missing table
    ("SELECT a FROM t t WHERE a = 1", False),             # duplicate table name
    ("SELECT a FROM , t WHERE a = 1", False),             # comma in FROM

    # ---------- WHERE boolean structure ----------
    ("SELECT a FROM t WHERE AND a = 1", False),           # leading AND
    ("SELECT a FROM t WHERE OR a = 1", False),            # leading OR
    ("SELECT a FROM t WHERE a = 1 AND", False),           # trailing AND
    ("SELECT a FROM t WHERE a = 1 OR", False),            # trailing OR
    ("SELECT a FROM t WHERE a = 1 AND OR b = 2", False),  # consecutive logical ops
    ("SELECT a FROM t WHERE a = 1 OR AND b = 2", False),  # reversed logical ops

    # ---------- WHERE comparison errors ----------
    ("SELECT a FROM t WHERE = 1", False),                 # missing LHS
    ("SELECT a FROM t WHERE a =", False),                 # missing RHS
    ("SELECT a FROM t WHERE a == 1", False),              # invalid comparator
    ("SELECT a FROM t WHERE a >< 1", False),              # invalid comparator
    ("SELECT a FROM t WHERE a => 1", False),              # invalid comparator
    ("SELECT a FROM t WHERE a <= >= 1", False),           # chained comparators

    # ---------- WHERE arithmetic errors ----------
    ("SELECT a FROM t WHERE a +", False),                 # dangling operator
    ("SELECT a FROM t WHERE + a = 1", False),             # unary not supported
    ("SELECT a FROM t WHERE a * / b > 1", False),         # invalid operator sequence
    ("SELECT a FROM t WHERE a + (b * ) > 1", False),      # empty sub-expression
    ("SELECT a FROM t WHERE a + () > 1", False),          # empty parentheses

    # ---------- Parentheses chaos ----------
    ("SELECT a FROM t WHERE ((a = 1)", False),            # missing close
    ("SELECT a FROM t WHERE (a = 1))", False),            # extra close
    ("SELECT a FROM t WHERE () AND a = 1", False),        # empty group
    ("SELECT a FROM t WHERE (AND a = 1)", False),         # invalid group
    ("SELECT a FROM t WHERE (a = 1 OR)", False),          # dangling OR in parens

    # ---------- Mixed SELECT + WHERE failures ----------
    ("SELECT a b FROM t WHERE a ==", False),              # both invalid
    ("SELECT * , a FROM t WHERE a + > 1", False),         # * misuse + bad expr
    ("SELECT a AS FROM t WHERE a > b < c", False),        # alias + comparison error
]




def run_tests():
    passed = 0
    failed = 0

    for i, (query, should_pass) in enumerate(TEST_CASES, 1):
        parser = QueryParser(query)
        result = parser.analyse()

        # ✅ CORRECT success detection
        success = result is None or (
            isinstance(result, dict) and result.get("status") == "ok"
        )

        if success == should_pass:
            print(f"[PASS {i}] {query}")
            passed += 1
        else:
            print(f"[FAIL {i}] {query}")
            print("  Expected:", "PASS" if should_pass else "FAIL")
            print("  Got:", result)
            failed += 1

    print("\nSummary:")
    print("Passed:", passed)
    print("Failed:", failed)



# run_tests()
while True:
    q = input("Enter sql query: ")
    parser = QueryParser(q)
    print(parser.analyse())