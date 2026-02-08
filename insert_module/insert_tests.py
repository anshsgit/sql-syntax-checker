from html import parser

from pydantic import validator
from insert_module.insert_parser import InsertParser
from insert_module.insert_validator import InsertValidator
from insert_module.insert_suggestions import InsertSuggester


def run_test(query: str):
    print("=" * 60)
    print("QUERY:")
    print(query)

    parser = InsertParser()
    validator = InsertValidator()
    suggester = InsertSuggester()
    
    parsed = parser.parse_insert(query)
    errors = validator.validate_insert(parsed)
    suggestion = suggester.suggest_insert_fix(query, parsed, errors)

    print("\nERRORS:")
    if not errors:
        print("No syntax errors found.")
    else:
        for error in errors:
            print(error)

    if suggestion:
        print("\nSUGGESTED FIX:")
        print(suggestion)

    print("=" * 60)
    print("\n")


def main():
    # Valid query
    run_test(
        "INSERT INTO students (id, name) VALUES (1, 'Alice');"
    )

    # Missing INTO
    run_test(
        "INSERT students VALUES (1);"
    )

    # Missing VALUES
    run_test(
        "INSERT INTO students (id, name);"
    )

    # Column-value mismatch
    run_test(
        "INSERT INTO students (id, name) VALUES (1);"
    )

    # Incorrect VALUES format
    run_test(
        "INSERT INTO students VALUES 1, 2;"
    )

    # Missing semicolon
    run_test(
        "INSERT INTO students (id, name) VALUES (1, 'Alice')"
    )

    # Invalid table name
    run_test(
        "INSERT INTO 123students (id, name) VALUES (1, 'Alice');"
    )

    # Invalid column name
    run_test(
        "INSERT INTO students (1id, name) VALUES (1, 'Alice');"
    )

    # Invalid value format
    run_test(
        "INSERT INTO students (id, name) VALUES (1, Alice);"
    )

    # Missing parentheses
    run_test(
        "INSERT INTO students id, name VALUES 1, 'Alice';"
    )

    # Extra values
    run_test(
        "INSERT INTO students (id, name) VALUES (1, 'Alice', 'Extra');"
    )

    # Edge case: Only keywords
    run_test(
        "INSERT INTO VALUES;"
    )

    # Edge case: No columns specified
    run_test(
        "INSERT INTO students VALUES (1, 'Alice');"
    )

    # Edge case: No values specified
    run_test(
        "INSERT INTO students (id, name) VALUES ();"
    )

    # Edge case: Mixed case keywords
    run_test(
        "insert into students (id, name) values (1, 'Alice');"
    )

    # Edge case: No Space Between Keywords
    run_test(
        "INSERTINTO students(id, name)VALUES(1, 'Alice');"
    )

    # Edge case: Missing Comma Between Columns
    run_test(
        "INSERT INTO students (id name) VALUES (1, 'Alice');"
    )

    # Edge case: Keywords repeated without space
    run_test(
        "INSERT INTOINTO students (id, name) VALUES (1, 'Alice');"
    )

    # Edge case: No space Query
    run_test(
        "INSERTINTOstudents(id,name)VALUES(1,'Alice');"
    )

    # Empty query
    run_test(
        ""
    )


if __name__ == "__main__":
    main()