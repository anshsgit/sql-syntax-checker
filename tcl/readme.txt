## TCL Syntax Checker Module

This module is responsible for validating SQL Transaction Control Language (TCL)
statements without executing them on any database.

Handled TCL Commands:

- COMMIT
- ROLLBACK
- SAVEPOINT

Objective:
The goal of this module is to detect syntax and structural errors in TCL statements
and provide clear, learner-friendly error explanations along with suggested fixes
wherever the correction is unambiguous.

Design Approach:

- Rule-based syntax validation
- No database connection or execution
- Class-based modular design
- Each TCL command has its own dedicated checker class

File Structure:

- commit_checker.py
  Validates COMMIT statement syntax and usage rules.

- rollback_checker.py
  Validates ROLLBACK and ROLLBACK TO savepoint syntax.

- savepoint_checker.py
  Validates SAVEPOINT statement syntax and naming rules.

- tcl_validator.py
  Acts as a central router that identifies the TCL command
  and forwards the query to the appropriate checker class.

Validation Strategy:

- Input SQL query is normalized (trimmed and converted to uppercase)
- Grammar rules are matched using keyword patterns
- Common syntax mistakes such as missing semicolons, missing keywords,
  and invalid formats are detected
- Errors are reported with:
  - What the error is
  - Why it is incorrect
  - Suggested fix (if applicable)

Example:
Input:
ROLLBACK sp1;

Output:
Error: Incorrect ROLLBACK syntax.
Reason: ROLLBACK requires the keyword 'TO' when referencing a savepoint.
Suggested fix: ROLLBACK TO sp1;

Limitations:

- Does not verify actual transaction state
- Does not check database-specific behavior
- Focuses strictly on syntax and structural rules

This module is designed to integrate with the overall SQL Grammar Checker
and helps users understand TCL usage without relying on database error messages.
