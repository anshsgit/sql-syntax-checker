import sys
import os

# Add the root directory to path to find other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Alter_module.alter import AlterCommand

def test_spell_checker():
    print("Running Spell Checker Verification...")
    
    test_cases = [
        {
            "name": "Typo in ALTER",
            "query": "ALTR TABLE users ADD age INT",
            "expected_suggestion": "Did you mean 'ALTER' instead of 'ALTR'?"
        },
        {
            "name": "Typo in TABLE",
            "query": "ALTER TABEL users ADD age INT",
            "expected_suggestion": "Did you mean 'TABLE' instead of 'TABEL'?"
        },
        {
            "name": "Typo in ADD",
            "query": "ALTER TABLE users ADDD age INT",
            "expected_suggestion": "Did you mean 'ADD' instead of 'ADDD'?"
        },
        {
            "name": "Typo in DROP",
            "query": "ALTER TABLE users DRQP COLUMN age",
            "expected_suggestion": "Did you mean 'DROP' instead of 'DRQP'?"
        },
        {
            "name": "Typo in MODIFY",
            "query": "ALTER TABLE users MODIF COLUMN age INT",
            "expected_suggestion": "Did you mean 'MODIFY' instead of 'MODIF'?"
        },
        {
            "name": "Typo in COLUMN",
            "query": "ALTER TABLE users ADD COLMN age INT",
            "expected_suggestion": "Did you mean 'COLUMN' instead of 'COLMN'?"
        },
         {
            "name": "Typo in TYPE",
            "query": "ALTER TABLE users ADD age INTEGR",
            "expected_suggestion": "Did you mean 'INTEGER' instead of 'INTEGR'?"
        }
    ]
    
    passed = 0
    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        checker = AlterCommand(case['query'])
        result = checker.validate()
        
        found = False
        for sugg in result['suggestions']:
            if case['expected_suggestion'] in sugg:
                found = True
                break
        
        if found:
            print(f"[PASS] PASSED. Found suggestion: {case['expected_suggestion']}")
            passed += 1
        else:
            print(f"[FAIL] FAILED. Expected suggestion: {case['expected_suggestion']}")
            print(f"Got suggestions: {result['suggestions']}")

    print(f"\nSummary: {passed}/{len(test_cases)} Passed")

if __name__ == "__main__":
    test_spell_checker()
