from QueryParser import QueryParser

TEST_CASES = [

    # =========================================================
    # 1. BASIC VALID QUERIES (sanity)
    # =========================================================
    ("SELECT a FROM t", True),
    ("SELECT a FROM t WHERE a = 1", True),
    ("SELECT * FROM t", True),
    ("SELECT a, b FROM t", True),
    ("SELECT a AS x FROM t", True),
    ("SELECT (a) FROM t", True),
    ("SELECT (a + b) FROM t", True),

    # =========================================================
    # 2. BASIC SELECT ERRORS
    # =========================================================
    ("SELECT FROM t", False),
    ("SELECT , a FROM t", False),
    ("SELECT a, FROM t", False),
    ("SELECT a b FROM t", False),
    ("SELECT * a FROM t", False),
    ("SELECT a AS 123 FROM t", False),
    ("SELECT a AS select FROM t", False),

    # =========================================================
    # 3. FROM CLAUSE ERRORS
    # =========================================================
    ("SELECT a WHERE a = 1", False),          # missing FROM
    ("SELECT a FROM WHERE a = 1", False),     # missing table
    ("SELECT a FROM , t WHERE a = 1", False),
    ("SELECT a FROM t t WHERE a = 1", False), # alias == table
    ("SELECT a FROM t, t WHERE a = 1", False),# duplicate table

    # =========================================================
    # 4. QUALIFIED COLUMNS
    # =========================================================
    ("SELECT t.a FROM t", True),
    ("SELECT t.a, t.b FROM t", True),
    ("SELECT (t.a + t.b) FROM t", True),

    ("SELECT x.a FROM t", False),              # unknown alias
    ("SELECT t. FROM t", False),
    ("SELECT .a FROM t", False),
    ("SELECT t.a.b FROM t", False),

    # =========================================================
    # 5. AGGREGATE FUNCTIONS
    # =========================================================
    ("SELECT SUM(a) FROM t", True),
    ("SELECT COUNT(*) FROM t", True),
    ("SELECT SUM(a + b) FROM t", True),
    ("SELECT SUM((a + b) * c) FROM t", True),

    ("SELECT SUM() FROM t", False),
    ("SELECT SUM(a,) FROM t", False),
    ("SELECT SUM(a b) FROM t", False),
    ("SELECT SUM(a AND b) FROM t", False),
    ("SELECT SUM(SUM(a)) FROM t", False),

    # =========================================================
    # 6. WHERE – SIMPLE COMPARISONS
    # =========================================================
    ("SELECT a FROM t WHERE a = 1", True),
    ("SELECT a FROM t WHERE a != 1", True),
    ("SELECT a FROM t WHERE a > 1", True),

    ("SELECT a FROM t WHERE", False),
    ("SELECT a FROM t WHERE a =", False),
    ("SELECT a FROM t WHERE = 1", False),
    ("SELECT a FROM t WHERE a == 1", False),

    # =========================================================
    # 7. WHERE – ARITHMETIC EXPRESSIONS
    # =========================================================
    ("SELECT a FROM t WHERE a + 1 > 2", True),
    ("SELECT a FROM t WHERE (a + b) * c > 10", True),
    ("SELECT a FROM t WHERE a + (b * (c + d)) > e", True),

    ("SELECT a FROM t WHERE a + > 1", False),
    ("SELECT a FROM t WHERE (a + ) > 1", False),
    ("SELECT a FROM t WHERE (a + ()) > 1", False),

    # =========================================================
    # 8. WHERE – LOGICAL EXPRESSIONS
    # =========================================================
    ("SELECT a FROM t WHERE a = 1 AND b = 2", True),
    ("SELECT a FROM t WHERE a = 1 OR b = 2", True),
    ("SELECT a FROM t WHERE (a = 1 OR b = 2) AND c = 3", True),

    ("SELECT a FROM t WHERE AND a = 1", False),
    ("SELECT a FROM t WHERE a = 1 AND", False),
    ("SELECT a FROM t WHERE a = 1 OR AND b = 2", False),

    # =========================================================
    # 9. BETWEEN / IN
    # =========================================================
    ("SELECT a FROM t WHERE a BETWEEN 1 AND 5", True),
    ("SELECT a FROM t WHERE a BETWEEN (b + 1) AND (c * 2)", True),
    ("SELECT a FROM t WHERE a IN (1, 2, 3)", True),
    ("SELECT a FROM t WHERE a IN ((1 + 2), (3 * 4))", True),

    ("SELECT a FROM t WHERE a BETWEEN 1", False),
    ("SELECT a FROM t WHERE a BETWEEN AND 5", False),
    ("SELECT a FROM t WHERE a IN ()", False),
    ("SELECT a FROM t WHERE a IN (1, , 2)", False),
    ("SELECT a FROM t WHERE a IN (1 AND 2)", False),

    # =========================================================
    # 10. AGGREGATE + WHERE INTEGRATION
    # =========================================================
    ("SELECT SUM(a) FROM t WHERE a > 1", True),
    ("SELECT SUM(a + b) FROM t WHERE a > 1", True),
    ("SELECT SUM(t.a * (t.b + t.c)) FROM t WHERE t.a > 10", True),

    ("SELECT SUM(a) FROM t WHERE SUM(a) > 1", False),

    # =========================================================
    # 11. DEEP NESTING (STRESS)
    # =========================================================
    ("SELECT (((a))) FROM t", True),
    ("SELECT ((a + b) * (c - d)) FROM t", True),
    ("SELECT a FROM t WHERE (((a + b) * c) > (d - e))", True),

    ("SELECT (((a)) FROM t", False),
    ("SELECT a FROM t WHERE (((a + b))", False),

    # =========================================================
    # 12. TOKEN BOUNDARY TORTURE
    # =========================================================
    ("SELECT ( t . a + ( t . b * t . c ) ) FROM t", True),
    ("SELECT t . a FROM t", True),

    ("SELECT t . FROM t", False),
    ("SELECT . a FROM t", False),
    ("SELECT t . a . b FROM t", False),

    # =========================================================
    # 13. INFINITE LOOP / STATE DESYNC DETECTORS
    # =========================================================
    ("SELECT (((((((a))))))) FROM t", True),
    ("SELECT (((a + b)))) FROM t", False),
    ("SELECT (a + (b * (c + (d * )))) FROM t", False),
    ("SELECT a FROM t WHERE (((((a = 1)))))", True),
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