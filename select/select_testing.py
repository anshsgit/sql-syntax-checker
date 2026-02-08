from QueryParser import QueryParser


TEST_CASES = [

# SELECT

("SELECT a FROM t", True),
("SELECT a, b FROM t", True),
("SELECT a AS x FROM t", True),
("SELECT * FROM t", True),

("SELECT FROM t", False),
("SELECT a FROM", False),
("SELECT a t", False),

("SELECT a FROM t WHERE a = 1", True),
("SELECT a FROM t WHERE a > 10", True),
("SELECT a FROM t WHERE a >= 10", True),

("SELECT a FROM t WHERE", False),
("SELECT a FROM t WHERE a =", False),
("SELECT a FROM t WHERE = 1", False),

("SELECT a FROM t WHERE a = 1 AND b = 2", True),
("SELECT a FROM t WHERE a = 1 OR b = 2", True),
("SELECT a FROM t WHERE (a = 1 OR b = 2) AND c = 3", True),

("SELECT a FROM t WHERE AND a = 1", False),
("SELECT a FROM t WHERE a = 1 OR", False),

("SELECT a FROM t WHERE a + 1 > 5", True),
("SELECT a FROM t WHERE (a * 2) + 1 > 5", True),

("SELECT a FROM t WHERE a + > 5", False),
("SELECT a FROM t WHERE a * * 2", False),

("SELECT SUM(a) FROM t", True),
("SELECT a, SUM(b) FROM t GROUP BY a", True),

("SELECT SUM(a) FROM t WHERE SUM(a) > 10", False),
("SELECT a, SUM(b) FROM t", False),

("SELECT a FROM t GROUP BY a", True),
("SELECT a + 1, SUM(b) FROM t GROUP BY a + 1", True),

("SELECT a, b FROM t GROUP BY a", False),
("SELECT SUM(b) FROM t GROUP BY a", False),

("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > 10", True),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING a > 1", True),

("SELECT a FROM t HAVING a > 1", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING b > 1", False),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (SUM(b) > 10 AND a > 1)",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (SUM(b) > 10 AND)",
 False
),

("SELECT a FROM t ORDER BY a", True),
("SELECT a FROM t ORDER BY a DESC", True),
("SELECT a FROM t ORDER BY a + 1", True),

("SELECT a FROM t ORDER BY", False),
("SELECT a FROM t ORDER BY DESC", False),

(
 "SELECT a, SUM(b) FROM t GROUP BY a ORDER BY a DESC",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a ORDER BY SUM(b) DESC",
 True
),

("SELECT a FROM t LIMIT 10", True),
("SELECT a FROM t LIMIT 0", True),

("SELECT a FROM t LIMIT", False),
("SELECT a FROM t LIMIT a", False),

(
 "SELECT t.a AS x, SUM(u.b) "
 "FROM t JOIN u ON t.id = u.id "
 "WHERE t.a > 1 "
 "GROUP BY t.a "
 "HAVING SUM(u.b) > 10 "
 "ORDER BY x DESC "
 "LIMIT 5",
 True
),

(
 "SELECT t.a, SUM(u.b) "
 "FROM t JOIN u ON t.id = u.id "
 "GROUP BY t.a "
 "HAVING u.b > 1",
 False
),

("SELECT a FROM t WHERE a = 1", True),
("SELECT a FROM t WHERE a > 1", True),
("SELECT a FROM t WHERE a < 1", True),
("SELECT a FROM t WHERE a >= 1", True),
("SELECT a FROM t WHERE a <= 1", True),

("SELECT a FROM t WHERE a =", False),
("SELECT a FROM t WHERE = 1", False),


# WHERE

("SELECT a FROM t WHERE a = b", True),
("SELECT a FROM t WHERE a != b", True),

("SELECT a FROM t WHERE a ! b", False),


("SELECT a FROM t WHERE a = 1 AND b = 2", True),
("SELECT a FROM t WHERE a = 1 OR b = 2", True),
("SELECT a FROM t WHERE a = 1 AND b = 2 OR c = 3", True),

("SELECT a FROM t WHERE AND a = 1", False),
("SELECT a FROM t WHERE a = 1 OR", False),


("SELECT a FROM t WHERE (a = 1)", True),
("SELECT a FROM t WHERE (a = 1 AND b = 2)", True),
("SELECT a FROM t WHERE (a = 1 OR b = 2) AND c = 3", True),

("SELECT a FROM t WHERE (a = 1", False),
("SELECT a FROM t WHERE a = 1)", False),

("SELECT a FROM t WHERE a + 1 > 2", True),
("SELECT a FROM t WHERE a * 2 = 10", True),
("SELECT a FROM t WHERE (a + 1) * 2 > 5", True),

("SELECT a FROM t WHERE a + > 2", False),
("SELECT a FROM t WHERE a * * 2", False),


(
 "SELECT a FROM t WHERE (a + 1 > 2 AND b * 2 < 10)",
 True
),

(
 "SELECT a FROM t WHERE ((a + 1) > (2 + 1))",
 True
),

(
 "SELECT a FROM t WHERE (a + 1 >)",
 False
),


("SELECT a FROM t WHERE t.a = 1", True),
("SELECT a FROM t JOIN u ON t.id = u.id WHERE u.b > 5", True),

("SELECT a FROM t WHERE x.a = 1", False),

("SELECT a FROM t WHERE SUM(a) > 1", False),
("SELECT a FROM t WHERE COUNT(*) = 1", False),


("SELECT a FROM t WHERE a BETWEEN 1 AND 10", True),
("SELECT a FROM t WHERE a IN (1, 2, 3)", True),

("SELECT a FROM t WHERE a BETWEEN 1", False),
("SELECT a FROM t WHERE a IN ()", False),

(
 "SELECT a FROM t WHERE (((a + 1) * (2 + 3)) > ((10)))",
 True
),

(
 "SELECT a FROM t WHERE (((a = 1 AND b = 2) OR (c = 3)))",
 True
),

(
 "SELECT a FROM t WHERE (((a = 1 AND) b = 2))",
 False
),



# =========================================================
# 1. BASIC FROM
# =========================================================
("SELECT a FROM t", True),
("SELECT a FROM table1", True),
("SELECT a FROM t AS x", True),
("SELECT a FROM t x", True),

("SELECT a FROM", False),
("SELECT a FROM 123", False),

# =========================================================
# 2. MULTIPLE TABLES (COMMA JOINS)
# =========================================================
("SELECT a FROM t, u", True),
("SELECT a FROM t, u, v", True),
("SELECT a FROM t AS x, u AS y", True),

("SELECT a FROM t,", False),
("SELECT a FROM , t", False),

# =========================================================
# 3. SIMPLE JOIN
# =========================================================
("SELECT a FROM t JOIN u ON t.id = u.id", True),
("SELECT a FROM t INNER JOIN u ON t.id = u.id", True),
("SELECT a FROM t LEFT JOIN u ON t.id = u.id", True),
("SELECT a FROM t RIGHT JOIN u ON t.id = u.id", True),
("SELECT a FROM t FULL JOIN u ON t.id = u.id", True),

("SELECT a FROM t JOIN u", False),
("SELECT a FROM t JOIN u ON", False),
("SELECT a FROM t JOIN u ON t.id =", False),

# =========================================================
# 4. JOIN ALIASING
# =========================================================
("SELECT a FROM t AS x JOIN u AS y ON x.id = y.id", True),
("SELECT a FROM t x JOIN u y ON x.id = y.id", True),

("SELECT a FROM t x JOIN u y ON t.id = u.id", False),
("SELECT a FROM t JOIN u ON x.id = u.id", False),

# =========================================================
# 5. MULTI-JOIN CHAINS
# =========================================================
(
 "SELECT a FROM t "
 "JOIN u ON t.id = u.id "
 "JOIN v ON u.id = v.id",
 True
),

(
 "SELECT a FROM t "
 "LEFT JOIN u ON t.id = u.id "
 "RIGHT JOIN v ON u.id = v.id",
 True
),

(
 "SELECT a FROM t "
 "JOIN u ON t.id = u.id "
 "JOIN u2 ON u.id = u2.id",
 True
),

# =========================================================
# 6. JOIN ERROR CASES
# =========================================================
(
 "SELECT a FROM t "
 "JOIN u ON t.id = x.id",
 False
),

(
 "SELECT a FROM t "
 "JOIN u ON t.id = u.id "
 "JOIN v ON x.id = v.id",
 False
),

# =========================================================
# 7. MIXING JOIN STYLES (DISALLOWED)
# =========================================================
("SELECT a FROM t, u JOIN v ON u.id = v.id", False),
("SELECT a FROM t JOIN u ON t.id = u.id, v", False),

# =========================================================
# 8. PARENTHESIS / ON CONDITIONS
# =========================================================
(
 "SELECT a FROM t "
 "JOIN u ON (t.id = u.id)",
 True
),

(
 "SELECT a FROM t "
 "JOIN u ON ((t.id = u.id AND u.b > 1))",
 True
),

(
 "SELECT a FROM t "
 "JOIN u ON (t.id =)",
 False
),

# =========================================================
# 9. SCHEMA-QUALIFIED TABLES
# =========================================================
("SELECT a FROM schema1.t", True),
("SELECT a FROM schema1.t AS x", True),
("SELECT a FROM schema1.t JOIN schema2.u ON t.id = u.id", False),

# =========================================================
# 10. TORTURE / EDGE CASES
# =========================================================
(
 "SELECT a FROM t "
 "JOIN u ON (((t.id))) = (((u.id)))",
 True
),

(
 "SELECT a FROM t "
 "JOIN u ON (t.id = u.id AND)",
 False
),

# =========================================================
("SELECT a FROM t GROUP BY a", True),
("SELECT a, SUM(b) FROM t GROUP BY a", True),
("SELECT a + 1, SUM(b) FROM t GROUP BY a + 1", True),

("SELECT a FROM t GROUP BY", False),
("SELECT a FROM t GROUP BY b", False),

# =========================================================
# 2. MULTI-COLUMN GROUP BY
# =========================================================
("SELECT a, b FROM t GROUP BY a, b", True),
("SELECT a, b, SUM(c) FROM t GROUP BY a, b", True),

("SELECT a, b FROM t GROUP BY a", False),
("SELECT a, b, SUM(c) FROM t GROUP BY a", False),

# =========================================================
# 3. AGGREGATES RULES
# =========================================================
("SELECT SUM(b) FROM t GROUP BY a", False),
("SELECT a FROM t GROUP BY SUM(a)", False),

("SELECT a, SUM(b) FROM t GROUP BY SUM(b)", False),

# =========================================================
# 4. EXPRESSIONS IN GROUP BY
# =========================================================
("SELECT a * 2, SUM(b) FROM t GROUP BY a * 2", True),
("SELECT (a + 1) * 2, SUM(b) FROM t GROUP BY (a + 1) * 2", True),

("SELECT a * 2, SUM(b) FROM t GROUP BY a", False),

# =========================================================
# 5. PARENTHESIS NORMALIZATION
# =========================================================
("SELECT (a) FROM t GROUP BY a", True),
("SELECT ((a)) FROM t GROUP BY (((a)))", True),

("SELECT (a + 1) FROM t GROUP BY a + 1", True),

# =========================================================
# 6. MULTIPLE AGGREGATES
# =========================================================
("SELECT a, SUM(b), COUNT(c) FROM t GROUP BY a", True),
("SELECT a, SUM(b), COUNT(c) FROM t GROUP BY a, b", False),

# =========================================================
# 7. GROUP BY WITH WHERE
# =========================================================
("SELECT a, SUM(b) FROM t WHERE a > 1 GROUP BY a", True),
("SELECT a, SUM(b) FROM t WHERE a > 1 GROUP BY a HAVING SUM(b) > 10", True),

# =========================================================
# 8. INVALID GROUP BY STRUCTURE
# =========================================================
("SELECT a, b FROM t GROUP BY", False),
("SELECT a, SUM(b) FROM t GROUP BY a,", False),

# =========================================================
# 9. QUALIFIED COLUMNS
# =========================================================
("SELECT t.a FROM t GROUP BY t.a", True),
("SELECT t.a, SUM(t.b) FROM t GROUP BY t.a", True),

("SELECT t.a, SUM(t.b) FROM t GROUP BY a", False),

# =========================================================
# 10. TORTURE / EDGE CASES
# =========================================================
(
 "SELECT (((a))), SUM(b) "
 "FROM t "
 "GROUP BY (((a)))",
 True
),

(
 "SELECT a + (1 * 2), SUM(b) "
 "FROM t "
 "GROUP BY (a + (1 * 2))",
 True
),

(
 "SELECT a + 1, SUM(b) "
 "FROM t "
 "GROUP BY ((a))",
 False
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a, SUM(b)",
 False
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a, (SUM(b))",
 False
),


# =========================================================
# 1–25 : HAVING (25 TEST CASES)
# =========================================================

# ---- Basic HAVING ----
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > 10", True),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING a > 1", True),
("SELECT a AS x, SUM(b) FROM t GROUP BY a HAVING x > 1", True),

("SELECT a FROM t HAVING a > 1", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING b > 1", False),

# ---- Boolean HAVING ----
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > 10 AND a > 1", True),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > 10 OR a > 1", True),

("SELECT a, SUM(b) FROM t GROUP BY a HAVING AND SUM(b) > 10", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > 10 AND", False),

# ---- Parentheses ----
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (SUM(b) > 10)",
 True
),
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING ((SUM(b) > 10 AND a > 1) OR (SUM(b) > 100))",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (a + 1 > 2)",
 False
),

# ---- Invalid expressions ----
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) >", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING >", False),

# ---- Qualified columns ----
(
 "SELECT t.a, SUM(t.b) FROM t GROUP BY t.a "
 "HAVING SUM(t.b) > 10",
 True
),
(
 "SELECT t.a, SUM(t.b) FROM t GROUP BY t.a "
 "HAVING t.b > 1",
 False
),

# ---- Deep nesting ----
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (((SUM(b))) > ((10)))",
 True
),
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING (((SUM(b)) > 10 AND))",
 False
),

# ---- Edge cases ----
("SELECT a, SUM(b) FROM t GROUP BY a HAVING", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING ()", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING (SUM(b))", False),
("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) = 10", True),


# =========================================================
# 26–55 : ORDER BY (30 TEST CASES)
# =========================================================

# ---- Basic ORDER BY ----
("SELECT a FROM t ORDER BY a", True),
("SELECT a FROM t ORDER BY a ASC", True),
("SELECT a FROM t ORDER BY a DESC", True),

("SELECT a FROM t ORDER BY", False),
("SELECT a FROM t ORDER BY DESC", False),

# ---- Arithmetic ORDER BY ----
("SELECT a FROM t ORDER BY a + 1", True),
("SELECT a FROM t ORDER BY (a * 2)", True),
("SELECT a FROM t ORDER BY (a + (1 * 2))", True),

("SELECT a FROM t ORDER BY a +", False),

# ---- ORDER BY aliases ----
("SELECT a AS x FROM t ORDER BY x", True),
("SELECT a AS x FROM t ORDER BY x DESC", True),

("SELECT a AS x FROM t ORDER BY y", False),

# ---- GROUP BY + ORDER BY ----
(
 "SELECT a, SUM(b) FROM t GROUP BY a ORDER BY a",
 True
),
(
 "SELECT a, SUM(b) FROM t GROUP BY a ORDER BY SUM(b)",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a ORDER BY b",
 False
),

# ---- Direction errors ----
("SELECT a FROM t ORDER BY a DESC ASC", False),
("SELECT a FROM t ORDER BY ASC", False),

# ---- Parentheses ----
("SELECT a FROM t ORDER BY (((a))) DESC", True),
("SELECT a FROM t ORDER BY ((a + 1))", True),

# ---- Complex ----
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING SUM(b) > 10 "
 "ORDER BY a DESC",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING SUM(b) > 10 "
 "ORDER BY SUM(b) DESC",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "ORDER BY (SUM(b) + 1)",
 False
),

# ---- Edge ----
("SELECT a FROM t ORDER BY , a", False),
("SELECT a FROM t ORDER BY ()", False),
("SELECT a FROM t ORDER BY (a AND b)", False),


# =========================================================
# 56–75 : LIMIT (20 TEST CASES)
# =========================================================

# ---- Valid LIMIT ----
("SELECT a FROM t LIMIT 10", True),
("SELECT a FROM t LIMIT 0", True),
("SELECT a FROM t ORDER BY a LIMIT 5", True),

# ---- Invalid LIMIT ----
("SELECT a FROM t LIMIT", False),
("SELECT a FROM t LIMIT a", False),
("SELECT a FROM t LIMIT -1", False),
("SELECT a FROM t LIMIT 10 20", False),

# ---- LIMIT with GROUP / HAVING / ORDER ----
(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING SUM(b) > 10 "
 "ORDER BY a DESC "
 "LIMIT 5",
 True
),

(
 "SELECT a, SUM(b) FROM t GROUP BY a "
 "HAVING SUM(b) > 10 "
 "LIMIT 5",
 True
),

# ---- Edge LIMIT ----
("SELECT a FROM t LIMIT 000", True),
("SELECT a FROM t LIMIT 01", True),

# ---- Bad placement ----
("SELECT a FROM t LIMIT 5 ORDER BY a", False),
("SELECT a FROM t HAVING a > 1 LIMIT 5", False),

# =========================================================
# 1. SIMPLE END-TO-END
# =========================================================
(
 "SELECT a FROM t "
 "WHERE a > 1 "
 "ORDER BY a "
 "LIMIT 5",
 True
),

(
 "SELECT a FROM t "
 "ORDER BY a "
 "LIMIT 5",
 True
),

(
 "SELECT a FROM t "
 "LIMIT 5",
 True
),

# =========================================================
# 2. JOIN + WHERE + ORDER + LIMIT
# =========================================================
(
 "SELECT t.a "
 "FROM t JOIN u ON t.id = u.id "
 "WHERE u.b > 10 "
 "ORDER BY t.a DESC "
 "LIMIT 3",
 True
),

(
 "SELECT t.a "
 "FROM t JOIN u ON t.id = u.id "
 "WHERE t.a > "
 "ORDER BY t.a "
 "LIMIT 3",
 False
),

# =========================================================
# 3. GROUP BY + HAVING + ORDER + LIMIT
# =========================================================
(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING SUM(b) > 10 "
 "ORDER BY a DESC "
 "LIMIT 5",
 True
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING a > 1 "
 "ORDER BY a "
 "LIMIT 5",
 True
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING b > 1 "
 "ORDER BY a "
 "LIMIT 5",
 False
),

# =========================================================
# 4. ALIASES EVERYWHERE
# =========================================================
(
 "SELECT t.a AS x, SUM(u.b) AS y "
 "FROM t JOIN u ON t.id = u.id "
 "GROUP BY t.a "
 "HAVING y > 10 "
 "ORDER BY x DESC "
 "LIMIT 5",
 True
),

(
 "SELECT t.a AS x, SUM(u.b) "
 "FROM t JOIN u ON t.id = u.id "
 "GROUP BY t.a "
 "HAVING x > 1 "
 "ORDER BY y DESC "
 "LIMIT 5",
 False
),

# =========================================================
# 5. BOOLEAN TORTURE
# =========================================================
(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING ((SUM(b) > 10 AND a > 1) "
 "OR (SUM(b) > 100 AND a > 5)) "
 "ORDER BY a "
 "LIMIT 10",
 True
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING ((SUM(b) > 10 AND)) "
 "ORDER BY a "
 "LIMIT 10",
 False
),

# =========================================================
# 6. EXPRESSION MATCHING
# =========================================================
(
 "SELECT (a + 1), SUM(b) "
 "FROM t "
 "GROUP BY (a + 1) "
 "HAVING SUM(b) > 5 "
 "ORDER BY (a + 1) "
 "LIMIT 3",
 True
),

(
 "SELECT (a + 1), SUM(b) "
 "FROM t "
 "GROUP BY a "
 "HAVING SUM(b) > 5 "
 "ORDER BY (a + 1) "
 "LIMIT 3",
 False
),

# =========================================================
# 7. ORDER BY AGGREGATES
# =========================================================
(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "ORDER BY SUM(b) DESC "
 "LIMIT 5",
 True
),

(
 "SELECT a, SUM(b) "
 "FROM t "
 "GROUP BY a "
 "ORDER BY (SUM(b) + 1)",
 False
),

# =========================================================
# 8. CLAUSE ORDER ENFORCEMENT
# =========================================================
(
 "SELECT a FROM t "
 "LIMIT 5 "
 "ORDER BY a",
 False
),

(
 "SELECT a FROM t "
 "HAVING a > 1 "
 "WHERE a = 1",
 False
),

# =========================================================
# 9. QUALIFIED COLUMN SCOPE
# =========================================================
(
 "SELECT t.a, SUM(u.b) "
 "FROM t JOIN u ON t.id = u.id "
 "WHERE t.a > 1 "
 "GROUP BY t.a "
 "HAVING SUM(u.b) > 10 "
 "ORDER BY t.a "
 "LIMIT 5",
 True
),

(
 "SELECT t.a, SUM(u.b) "
 "FROM t JOIN u ON t.id = u.id "
 "WHERE x.a > 1 "
 "GROUP BY t.a "
 "HAVING SUM(u.b) > 10 "
 "ORDER BY t.a "
 "LIMIT 5",
 False
),

# =========================================================
# 10. DEEP NESTING / NORMALIZATION
# =========================================================
(
 "SELECT (((a))), SUM(b) "
 "FROM t "
 "GROUP BY (((a))) "
 "HAVING (((SUM(b))) > ((10))) "
 "ORDER BY (((a))) DESC "
 "LIMIT 1",
 True
),

(
 "SELECT (((a))), SUM(b) "
 "FROM t "
 "GROUP BY (((a))) "
 "HAVING (((SUM(b)) + 1) > 10) "
 "ORDER BY (((a))) "
 "LIMIT 1",
 False
),

    ("SELECT a FROM t WHERE a > (SELECT MAX(b) FROM u)", True),
    ("SELECT a FROM t WHERE a = (SELECT MIN(b) FROM u)", True),
    ("SELECT a FROM t WHERE a >= (SELECT COUNT(b) FROM u)", True),
    ("SELECT a FROM t WHERE a < ((SELECT AVG(b) FROM u))", True),

    # -------------------------------------------------
    # 2. Scalar subqueries in SELECT list (VALID)
    # -------------------------------------------------
    ("SELECT (SELECT MAX(b) FROM u) FROM t", True),
    ("SELECT a, (SELECT MIN(b) FROM u) FROM t", True),
    ("SELECT (SELECT COUNT(*) FROM u) AS c FROM t", True),

    # -------------------------------------------------
    # 3. Scalar subqueries in HAVING (VALID)
    # -------------------------------------------------
    ("SELECT a, SUM(b) FROM t GROUP BY a HAVING SUM(b) > (SELECT AVG(c) FROM u)", True),
    ("SELECT a FROM t GROUP BY a HAVING a > (SELECT MIN(x) FROM u)", True),

    # -------------------------------------------------
    # 4. IN subqueries (VALID)
    # -------------------------------------------------
    ("SELECT a FROM t WHERE a IN (SELECT x FROM u)", True),
    ("SELECT a FROM t WHERE a NOT IN (SELECT x FROM u)", True),
    ("SELECT a FROM t WHERE a IN ((SELECT x FROM u))", True),

    # -------------------------------------------------
    # 5. IN subquery violations (INVALID)
    # -------------------------------------------------
    ("SELECT a FROM t WHERE a IN ()", False),
    ("SELECT a FROM t WHERE a IN SELECT x FROM u", False),
    ("SELECT a FROM t WHERE a IN (SELECT x, y FROM u)", False),

    # -------------------------------------------------
    # 6. Invalid scalar subqueries (INVALID)
    # -------------------------------------------------
    ("SELECT a FROM t WHERE a > (SELECT x, y FROM u)", False),   # multi-column
    ("SELECT a FROM t WHERE (SELECT MAX(b) FROM u) + 1 > 10", False),
    ("SELECT a FROM t WHERE a + (SELECT b FROM u) > 1", False),

    # -------------------------------------------------
    # 7. Derived tables (FROM subqueries) – VALID
    # -------------------------------------------------
    ("SELECT x FROM (SELECT a AS x FROM t) sub", True),
    ("SELECT sub.x FROM (SELECT a AS x FROM t) sub", True),
    ("SELECT a FROM (SELECT a FROM t) t2", True),

    # -------------------------------------------------
    # 8. Derived table violations (INVALID)
    # -------------------------------------------------
    ("SELECT a FROM (SELECT a FROM t)", False),     # missing alias
    ("SELECT a FROM (a FROM t) sub", False),        # invalid subquery

    # -------------------------------------------------
    # 9. Unsupported (correlated subqueries) – INVALID
    # -------------------------------------------------
    ("SELECT a FROM t WHERE a IN (SELECT x FROM u WHERE u.b = t.b)", False),
    ("SELECT a FROM t WHERE a > (SELECT b FROM u WHERE u.c = t.c)", False),

    # -------------------------------------------------
    # 10. ORDER BY subqueries (INVALID)
    # -------------------------------------------------
    ("SELECT a FROM t ORDER BY (SELECT MAX(b) FROM u)", False),

]



from QueryParser import QueryParser


def run_tests(TEST_CASES, save_report=False, report_file="test_report.txt"):
    passed = 0
    failed = 0
    failed_cases = []

    for i, (query, should_pass) in enumerate(TEST_CASES, 1):
        parser = QueryParser(query)
        result = parser.analyse()

        # success = no error returned
        success = result is None or (
            isinstance(result, dict) and result.get("status") == "ok"
        )

        if success == should_pass:
            passed += 1
        else:
            failed += 1
            failed_cases.append({
                "id": i,
                "query": query,
                "expected": "PASS" if should_pass else "FAIL",
                "got": "PASS" if success else "FAIL",
                "error": result
            })

    # ================= REPORT =================
    print("=" * 70)
    print("SQL PARSER TEST REPORT")
    print("=" * 70)
    print(f"Total tests   : {len(TEST_CASES)}")
    print(f"Passed        : {passed}")
    print(f"Failed        : {failed}")
    print(f"Success rate  : {passed / len(TEST_CASES) * 100:.2f}%")
    print("=" * 70)

    if failed_cases:
        print("\nFAILED CASES:")
        print("-" * 70)
        for case in failed_cases:
            print(f"[{case['id']}] {case['query']}")
            print(f"  Expected : {case['expected']}")
            print(f"  Got      : {case['got']}")
            print(f"  Error    : {case['error']}")
            print("-" * 70)

    # ================= SAVE REPORT =================
    if save_report:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("SQL PARSER TEST REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total tests   : {len(TEST_CASES)}\n")
            f.write(f"Passed        : {passed}\n")
            f.write(f"Failed        : {failed}\n")
            f.write(f"Success rate  : {passed / len(TEST_CASES) * 100:.2f}%\n")
            f.write("=" * 70 + "\n\n")

            if failed_cases:
                f.write("FAILED CASES:\n")
                f.write("-" * 70 + "\n")
                for case in failed_cases:
                    f.write(f"[{case['id']}] {case['query']}\n")
                    f.write(f"  Expected : {case['expected']}\n")
                    f.write(f"  Got      : {case['got']}\n")
                    f.write(f"  Error    : {case['error']}\n")
                    f.write("-" * 70 + "\n")

        print(f"\n📄 Report saved to: {report_file}")

    return passed, failed, failed_cases

run_tests(TEST_CASES, save_report=True)
