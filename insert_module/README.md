# INSERT Query Syntax Analyzer

## Overview

This module is part of the **SQL Syntax Checker** project. It focuses exclusively on analyzing **INSERT SQL queries** and detecting **syntax and structural errors** without connecting to or executing against any database.

The goal is not just to say that a query is wrong, but to clearly explain:

* **What** the error is
* **Why** it is incorrect according to SQL grammar
* **Where** it occurs in the query
* **How** it can be fixed (when the fix is unambiguous)

This module is designed to be **learner-friendly**, readable, and easy to extend.

---

## Folder Structure

```
insert/
├── __init__.py
├── insert_parser.py
├── insert_validator.py
├── insert_errors.py
├── insert_suggestions.py
├── insert_tests.py
└── README.md
```

Each file has a **single, well-defined responsibility**, following clean modular design principles.

---

## Design Philosophy

The INSERT analyzer is built using a **three-layer approach**:

1. **Parsing** – Extracts structure from the raw query
2. **Validation** – Applies SQL grammar rules and detects errors
3. **Suggestions** – Provides corrected queries when the fix is obvious

This separation ensures clarity, maintainability, and meaningful error explanations.

---

## 1. insert_parser.py

### Purpose

Extracts the basic structure of an INSERT query **without validating correctness**.

### Responsibilities

* Identify table name
* Extract column list (if provided)
* Extract VALUES data (supports multiple rows)

### Key Design Choice

* **No regular expressions are used**
* Parsing is done using string operations (`split`, `find`, slicing)

This makes the parser:

* Easier to understand
* Easier to debug
* Easier to explain in academic evaluation

The parser is intentionally tolerant and does not throw errors. All correctness checks are delegated to the validator.

---

## 2. insert_validator.py

### Purpose

Applies SQL grammar rules to the parsed output and detects syntax and structural errors.

### Validation Rules Implemented

* Query must start with `INSERT`
* `INTO` keyword must be present
* Table name must be specified
* `VALUES` clause must exist
* VALUES must be enclosed in parentheses
* Column count must match value count (if columns are specified)
* VALUES list must not be empty
* Keywords must be properly separated (e.g., `INSERT INTO`, not `INSERTINTO`)

> The validator focuses on **structural SQL correctness**, not semantic validation (e.g., column names, data types).

### Error Handling

* Multiple errors can be reported at once
* Each error includes:

  * Error message
  * Explanation
  * Approximate location

This ensures feedback is **clear and educational**, not cryptic.

---

## 3. insert_errors.py

### Purpose

Defines a structured error representation using the `InsertError` class.

### Why This Matters

Instead of returning plain strings, errors are represented as objects containing:

* `message`
* `explanation`
* `position`

This allows:

* Consistent error formatting
* Easy extension (severity, error codes, UI integration)
* Reuse across other query modules (SELECT, UPDATE, etc.)

---

## 4. insert_suggestions.py

### Purpose

Generates **corrected SQL suggestions** when the fix is clear and unambiguous.

### Supported Suggestions

* Adding missing `INTO`
* Adding missing `VALUES`
* Fixing malformed VALUES clauses
* Resolving column–value count mismatches (using placeholders)

### Design Principle

Suggestions are **conservative**:

* The system never guesses table names, column names, or values
* Placeholders like `(...)` are used when needed
* Suggestions are skipped when multiple interpretations are possible

---

## 5. insert_tests.py

### Purpose

Demonstrates and verifies the behavior of the INSERT analyzer.

### Characteristics

* No external testing framework
* Uses simple print-based output
* Covers:

  * Valid queries
  * Missing keywords
  * Malformed VALUES clauses
  * Column–value count mismatches
  * Empty input

This makes the module easy to test, debug, and demonstrate during evaluation.

---

## Edge Case Handling

### Handled

* Case-insensitive SQL keywords
* Extra or inconsistent whitespace
* Missing clauses (`INTO`, `VALUES`)
* Column–value mismatches
* Empty VALUES lists
* Missing or optional semicolons

### Known Edge Cases (Limitations)

* Repeated keywords without separators (e.g., `INTOINTO`) may not always be flagged
* Grammatically invalid identifiers (e.g., `123students`, `1id`) are not validated
* Value type correctness (e.g., quoted vs unquoted strings) is not enforced
* Some malformed queries without spacing may bypass detection depending on token structure

These limitations are intentional to keep the module **syntax-focused**, readable, and suitable for academic demonstration.

---

## Conclusion

The INSERT module provides a clean, modular, and educational approach to SQL syntax analysis. By separating parsing, validation, error representation, and suggestions, it achieves:

* Clear error explanations
* Maintainable code structure
* Easy extensibility for future enhancements

This module serves as a strong foundation for building analyzers for other SQL query types.