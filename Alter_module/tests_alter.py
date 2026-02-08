import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from alter import AlterCommand

def run_test(name, query, expected_valid, expected_errors=[]):
    print(f"Running Test: {name}")
    print(f"Query: {query}")
    
    checker = AlterCommand(query)
    result = checker.validate()
    
    if result["valid"] == expected_valid:
        # If expected invalid, check if errors match roughly
        if not expected_valid:
            if any(e in str(result["errors"]) for e in expected_errors):
                 print(f"[PASS] PASSED (Invalid as expected. Errors: {result['errors']})")
                 return True
            elif not expected_errors:
                 print(f"[PASS] PASSED (Invalid as expected)")
                 return True
            else:
                 print(f"[FAIL] FAILED. Expected errors like {expected_errors}, got {result['errors']}")
                 return False
        else:
             print("[PASS] PASSED (Valid)")
             return True
    else:
        print(f"[FAIL] FAILED. Expected Valid: {expected_valid}, Got: {result['valid']}")
        print(f"Errors: {result['errors']}")
        print(f"Suggestions: {result['suggestions']}")
        return False
    print("-" * 40)

def main():
    tests = [
        {
            "name": "Valid ADD Column",
            "query": "ALTER TABLE users ADD age INT",
            "expected_valid": True
        },
        {
            "name": "Valid DROP Column",
            "query": "ALTER TABLE users DROP COLUMN email",
            "expected_valid": True
        },
        {
            "name": "Valid MODIFY Column",
            "query": "ALTER TABLE employees MODIFY COLUMN salary DECIMAL(10,2)",
            "expected_valid": True
        },
        {
            "name": "Multiple Operations (ADD, DROP)",
            "query": "ALTER TABLE products ADD stock INT, DROP COLUMN obsolete_col",
            "expected_valid": True
        },
        {
            "name": "Missing Table Name",
            "query": "ALTER TABLE ADD age INT",
            "expected_valid": False,
            "expected_errors": ["Invalid ALTER TABLE syntax"]
        },
        {
            "name": "Invalid Column Type",
            "query": "ALTER TABLE users ADD name UNKNOWN_TYPE",
            "expected_valid": False,
            "expected_errors": ["Invalid or unsupported data type"]
        },
        {
            "name": "Missing Sub-command",
            "query": "ALTER TABLE users",
            "expected_valid": False,
            "expected_errors": ["Invalid ALTER TABLE syntax"]
        },
        {
            "name": "Incomplete ADD",
            "query": "ALTER TABLE users ADD",
            "expected_valid": False,
            "expected_errors": ["Incomplete ADD command"]
        },
        {
            "name": "Case Insensitivity",
            "query": "alter table USERS add AGE int",
            "expected_valid": True
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for t in tests:
        if run_test(t["name"], t["query"], t["expected_valid"], t.get("expected_errors", [])):
            passed += 1
        print("-" * 40)
            
    print(f"\nTest Summary: {passed}/{total} Passed")
    
if __name__ == "__main__":
    main()
