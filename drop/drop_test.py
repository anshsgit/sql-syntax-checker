from drop.DropDDL import DropDDL

# VALID DROP QUERIES

valid_drop_queries = [

    # DROP TABLE
    "DROP TABLE users;",
    "DROP TABLE users",
    "DROP TABLE IF EXISTS users;",
    "DROP TABLE users, orders;",
    "DROP TABLE users , orders ;",
    "DROP TABLE public.users;",
    "DROP TABLE schema1.table1, schema2.table2;",
    'DROP TABLE "User Table";',
    'DROP TABLE "schema"."table";',
    'DROP TABLE IF EXISTS "User-Data";',
    "DROP TABLE users CASCADE;",
    "DROP TABLE users RESTRICT;",
    "DROP TABLE IF EXISTS users CASCADE;",

    # DROP VIEW
    "DROP VIEW user_view;",
    "DROP VIEW IF EXISTS user_view;",
    "DROP VIEW public.user_view;",
    'DROP VIEW "Order Details";',
    "DROP VIEW v1, v2;",
    "DROP VIEW v1, v2 CASCADE;",
    "DROP VIEW v1 RESTRICT;",

    # DROP INDEX
    "DROP INDEX idx_users;",
    "DROP INDEX IF EXISTS idx_users;",
    "DROP INDEX public.idx_users;",
    'DROP INDEX "Users Index";',
    "DROP INDEX idx1, idx2;",
    "DROP INDEX idx_users CASCADE;",
    "DROP INDEX idx_users RESTRICT;",

    # DROP DATABASE
    "DROP DATABASE testdb;",
    "DROP DATABASE testdb",
    "DROP DATABASE IF EXISTS testdb;",
    "DROP DATABASE main_db;",
    'DROP DATABASE "Test Database";',
    'DROP DATABASE "123db";',
]


# INVALID DROP QUERIES (COMMON USER ERRORS)

invalid_drop_queries = [

    # Empty / Incomplete
    "",
    "   ",
    "DROP;",
    "DROP TABLE;",
    "DROP VIEW;",
    "DROP INDEX;",
    "DROP DATABASE;",

    # Wrong keywords
    "DELETE TABLE users;",
    "DROP TABLES users;",
    "DROP DATABASES testdb;",
    "REMOVE TABLE users;",

    # IF EXISTS misuse
    "DROP TABLE IF users;",
    "DROP DATABASE EXISTS testdb;",
    "DROP VIEW IF users;",

    # Invalid identifiers
    "DROP TABLE 123users;",
    "DROP TABLE @users;",
    "DROP VIEW users$;",
    "DROP INDEX idx$;",
    "DROP DATABASE 123db;",

    # Schema errors
    "DROP TABLE schema..table;",
    "DROP TABLE .users;",
    "DROP TABLE users.;",

    # Comma misuse
    "DROP TABLE users,,orders;",
    "DROP TABLE ,users;",
    "DROP TABLE users,;",
    "DROP VIEW v1,,v2;",

    # Database-specific errors
    "DROP DATABASE testdb, otherdb;",
    "DROP DATABASE testdb otherdb;",

    # CASCADE / RESTRICT misuse
    "DROP TABLE users CASCADE CASCADE;",
    "DROP TABLE users CASCADE RESTRICT;",
    "DROP DATABASE testdb CASCADE;",

    # Garbage / invalid structure
    "DROP TABLE users orders;",
    "DROP VIEW IF EXISTS;",
    "DROP INDEX IF EXISTS;",
    "DROP TABLE users WHERE id = 1;",
    "DROP TABLE users; DROP TABLE orders;",
]


# UNSUPPORTED BUT REALISTIC QUERIES (KNOWN LIMITATIONS)

unsupported_queries = [

    "DROP TABLE ONLY users;",
    "DROP INDEX CONCURRENTLY idx_users;",
    "DROP MATERIALIZED VIEW my_view;",
    'DROP TABLE "User""Table";',
    "DROP TABLE users -- comment",
]


#RUN TESTS

total_tests = 0
failed_tests = []

print("\n===== DROP QUERY TEST RESULTS =====\n")


#VALID QUERIES
print("---- VALID QUERIES ----\n")
for query in valid_drop_queries:
    total_tests += 1
    valid, message = DropDDL.validateDropQuery(query)

    if valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))


#INVALID QUERIES
print("\n---- INVALID QUERIES ----\n")
for query in invalid_drop_queries:
    total_tests += 1
    valid, message = DropDDL.validateDropQuery(query)

    if not valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> Should be invalid but passed")
        failed_tests.append((query, "Should be invalid but passed"))


#UNSUPPORTED (FUTURE SCOPE)
print("\n---- UNSUPPORTED (KNOWN LIMITATIONS) ----\n")
for query in unsupported_queries:
    total_tests += 1
    valid, message = DropDDL.validateDropQuery(query)
    print(f"[INFO] {query} -> Not supported by design")


#TEST SUMMARY

print("\n===== TEST SUMMARY =====")
print(f"Total Test Cases : {total_tests}")
print(f"Passed           : {total_tests - len(failed_tests)}")
print(f"Failed           : {len(failed_tests)}")

if failed_tests:
    print("\n--- Failed Test Descriptions ---")
    for i, (q, msg) in enumerate(failed_tests, start=1):
        print(f"{i}. Query : {q}")
        print(f"   Message: {msg}")
else:
    print("\nAll supported DROP tests passed successfully.")
