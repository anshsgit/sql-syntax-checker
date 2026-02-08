from truncate.TruncateDDL import TruncateDDL

#VALID TRUNCATE QUERIES

valid_truncate_queries = [

    #BASIC
    "TRUNCATE TABLE users;",
    "TRUNCATE TABLE users",
    "TRUNCATE TABLE public.users;",
    'TRUNCATE TABLE "Order Details";',

    #IDENTITY OPTIONS
    "TRUNCATE TABLE users RESTART IDENTITY;",
    "TRUNCATE TABLE users CONTINUE IDENTITY;",

    #REFERENTIAL OPTIONS
    "TRUNCATE TABLE users CASCADE;",
    "TRUNCATE TABLE users RESTRICT;",

    #COMBINED OPTIONS
    "TRUNCATE TABLE users RESTART IDENTITY CASCADE;",
    "TRUNCATE TABLE users CONTINUE IDENTITY RESTRICT;",

    #WHITESPACE VARIANTS
    "  TRUNCATE   TABLE   users   RESTART   IDENTITY   ;",
]


#INVALID TRUNCATE QUERIES

invalid_truncate_queries = [

    # EMPTY / INCOMPLETE
    "",
    "TRUNCATE;",
    "TRUNCATE TABLE;",
    "TRUNCATE users;",

    # INVALID IDENTIFIERS
    "TRUNCATE TABLE 123users;",
    "TRUNCATE TABLE users$;",
    "TRUNCATE TABLE schema..table;",

    # IDENTITY ERRORS
    "TRUNCATE TABLE users RESTART;",
    "TRUNCATE TABLE users CONTINUE;",
    "TRUNCATE TABLE users RESTART IDENTITY RESTART IDENTITY;",

    # REFERENTIAL ERRORS
    "TRUNCATE TABLE users CASCADE CASCADE;",
    "TRUNCATE TABLE users RESTRICT RESTRICT;",

    # INVALID ORDER / TOKENS
    "TRUNCATE TABLE users IDENTITY;",
    "TRUNCATE TABLE users DROP;",
    "TRUNCATE TABLE users CASCADE IDENTITY;",

    # EXTRA GARBAGE
    "TRUNCATE TABLE users EXTRA;",
    "TRUNCATE TABLE users RESTART IDENTITY EXTRA;",

    # EDGE CASES
    "TRUNCATE TABLE ;",
    "   ",
]


#RUN TESTS

failed_tests = []
total_tests = 0

print("\n===== TRUNCATE QUERY TEST RESULTS =====\n")

#VALID TESTS
for query in valid_truncate_queries:
    total_tests += 1
    valid, message = TruncateDDL.validateTruncateQuery(query)

    if valid:
        print(f"[PASS] {query}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))


#INVALID TESTS
for query in invalid_truncate_queries:
    total_tests += 1
    valid, message = TruncateDDL.validateTruncateQuery(query)

    if not valid:
        print(f"[PASS] {query} (Correctly Rejected)")
    else:
        print(f"[FAIL] {query} (Expected failure: {message})")
        failed_tests.append((query, "Should be invalid but passed"))


#TEST SUMMARY

print("\n===== TEST SUMMARY =====")
print(f"Total Test Cases : {total_tests}")
print(f"Passed           : {total_tests - len(failed_tests)}")
print(f"Failed           : {len(failed_tests)}")

if failed_tests:
    print("\n--- Failed Test Descriptions ---")
    for i, (q, msg) in enumerate(failed_tests, start=1):
        print(f"{i}. Query : {q}")
        print(f"   Issue : {msg}")
else:
    print("\nAll TRUNCATE tests passed successfully.")
