from create.CreateDDL import CreateDDL


#VALID CREATE DATABASE QUERIES

valid_create_database_queries = [
    "CREATE DATABASE testdb;",
    "CREATE DATABASE testdb",
    "CREATE DATABASE IF NOT EXISTS my_db;",
    'CREATE DATABASE "Test Database";',
    'CREATE DATABASE "123db";',
]


#INVALID CREATE DATABASE QUERIES

invalid_create_database_queries = [
    "",
    "   ",
    "CREATE DATABASE;",
    "CREATE DATABASE 123db;",
    "CREATE DATABASE testdb extra;",
    "CREATE DATABASE IF EXISTS testdb;",
]


#VALID CREATE TABLE QUERIES

valid_create_table_queries = [
    # Basic
    "CREATE TABLE users (id INT);",
    "CREATE TABLE users (id INT, name TEXT);",
    "CREATE TABLE IF NOT EXISTS public.users (id INT);",
    'CREATE TABLE "User Table" ("User Id" INT);',

    # NOT NULL / DEFAULT
    "CREATE TABLE users (id INT NOT NULL);",
    "CREATE TABLE users (id INT DEFAULT 0);",
    "CREATE TABLE users (id INT NOT NULL DEFAULT 1);",

    # PRIMARY KEY
    "CREATE TABLE users (id INT PRIMARY KEY);",
    "CREATE TABLE users (id INT, PRIMARY KEY (id));",

    # UNIQUE
    "CREATE TABLE users (email TEXT UNIQUE);",
    "CREATE TABLE users (email TEXT, UNIQUE (email));",

    # CHECK
    "CREATE TABLE users (age INT CHECK (age > 18));",
    "CREATE TABLE users (age INT, CHECK (age > 18));",

    # FOREIGN KEY / REFERENCES
    "CREATE TABLE orders (user_id INT REFERENCES users(id));",
    "CREATE TABLE orders (user_id INT, FOREIGN KEY (user_id) REFERENCES users(id));",

    # Combined
    "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));",
]


#INVALID CREATE TABLE QUERIES

invalid_create_table_queries = [
    "",
    "   ",
    "CREATE TABLE;",
    "CREATE TABLE users;",
    "CREATE TABLE users ();",
    "CREATE TABLE users, orders (id INT);",

    # Identifier errors
    "CREATE TABLE 1users (id INT);",
    "CREATE TABLE users$ (id INT);",
    'CREATE TABLE "" (id INT);',

    # Column errors
    "CREATE TABLE users (id);",
    "CREATE TABLE users (1id INT);",
    "CREATE TABLE users (id INT,);",

    # Constraint errors
    "CREATE TABLE users (id INT PRIMARY);",
    "CREATE TABLE users (age INT CHECK age > 18);",
    "CREATE TABLE users (id INT DEFAULT);",
    "CREATE TABLE orders (user_id INT REFERENCES);",
    "CREATE TABLE orders (FOREIGN KEY REFERENCES users(id));",

    # Syntax errors
    "CREATE TABLE users (id INT CHECK (id > 0);",
    "CREATE TABLE users (id INT) EXTRA;",
]


#VALID CREATE VIEW QUERIES

valid_create_view_queries = [
    "CREATE VIEW v_users AS SELECT * FROM users;",
    "CREATE OR REPLACE VIEW sales_view AS SELECT id FROM sales;",
    'CREATE VIEW "User View" AS SELECT name FROM users;',
    "CREATE VIEW v (id, name) AS SELECT id, name FROM users;",
]


#INVALID CREATE VIEW QUERIES

invalid_create_view_queries = [
    "",
    "   ",
    "CREATE VIEW;",
    "CREATE VIEW v AS;",
    "CREATE VIEW 123v AS SELECT * FROM t;",
    "CREATE VIEW v SELECT * FROM t;",
    "CREATE VIEW v AS INSERT INTO t VALUES (1);",
    "CREATE VIEW v (id,) AS SELECT id FROM t;",
]


#VALID CREATE INDEX QUERIES

valid_create_index_queries = [
    "CREATE INDEX idx_users_id ON users(id);",
    "CREATE UNIQUE INDEX idx_email ON users(email);",
    'CREATE INDEX "idx name" ON "User Table" ("User Name");',
    "CREATE INDEX idx_multi ON users(id, name DESC);",
]


#INVALID CREATE INDEX QUERIES

invalid_create_index_queries = [
    "",
    "   ",
    "CREATE INDEX;",
    "CREATE INDEX ON users(id);",
    "CREATE INDEX idx users(id);",
    "CREATE INDEX idx ON users;",
    "CREATE INDEX idx ON users(id UP);",
    "CREATE INDEX idx ON users(id,);",
]


#UNSUPPORTED CREATE TABLE QUERIES (ANSI SQL 2019 FEATURES)

unsupported_create_table_queries = [
    "CREATE TABLE users (id INT GENERATED ALWAYS AS IDENTITY);",
    "CREATE TABLE users (id SERIAL);",
    "CREATE TABLE users (created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
    "CREATE TABLE orders (user_id INT REFERENCES users(id) ON DELETE CASCADE);",
    "CREATE TABLE orders (user_id INT REFERENCES users(id) DEFERRABLE);",
]


#RUN TESTS

failed_tests = []
total_tests = 0

print("\n===== CREATE QUERY TEST RESULTS =====\n")


#CREATE DATABASE
print("---- CREATE DATABASE ----\n")

for query in valid_create_database_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateDatabaseQuery(query)
    if valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))

for query in invalid_create_database_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateDatabaseQuery(query)
    if not valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> Should be invalid but passed")
        failed_tests.append((query, "Should be invalid but passed"))


#CREATE TABLE
print("\n---- CREATE TABLE ----\n")

for query in valid_create_table_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateTableQuery(query)
    if valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))

for query in invalid_create_table_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateTableQuery(query)
    if not valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> Should be invalid but passed")
        failed_tests.append((query, "Should be invalid but passed"))


#CREATE VIEW
print("\n---- CREATE VIEW ----\n")

for query in valid_create_view_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateViewQuery(query)
    if valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))

for query in invalid_create_view_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateViewQuery(query)
    if not valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> Should be invalid but passed")
        failed_tests.append((query, "Should be invalid but passed"))


#CREATE INDEX
print("\n---- CREATE INDEX ----\n")

for query in valid_create_index_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateIndexQuery(query)
    if valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> {message}")
        failed_tests.append((query, message))

for query in invalid_create_index_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateIndexQuery(query)
    if not valid:
        print(f"[PASS] {query} -> {message}")
    else:
        print(f"[FAIL] {query} -> Should be invalid but passed")
        failed_tests.append((query, "Should be invalid but passed"))


#UNSUPPORTED CREATE TABLE (INFO ONLY)
print("\n---- CREATE TABLE (UNSUPPORTED FEATURES) ----\n")

for query in unsupported_create_table_queries:
    total_tests += 1
    valid, message = CreateDDL.validateCreateTableQuery(query)
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
    print("\nAll CREATE tests passed successfully.")
