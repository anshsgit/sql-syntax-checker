import re
import sys
import os

# Add the parent directory (root) to sys.path to verify imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spell_checker.utils import SpellChecker

class DeleteCommand:
    def __init__(self, query):
        self.query = query.strip()
        self.table_name = None
        self.delete_pattern = re.compile(
            r"^DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s*(.*))?;?$",
            re.IGNORECASE | re.DOTALL
        )

    def validate(self):
        if not self.query:
            return {
                "error": "Empty query.",
                "suggestion": "Provide a DELETE statement."
            }

        match = self.delete_pattern.match(self.query)

        if not match:
            first_word = self.query.split()[0].upper()

            if first_word != "DELETE":
                sugg = SpellChecker.check(first_word)
                return {
                    "error": "Query must start with DELETE.",
                    "suggestion": f"Did you mean '{sugg[0]}'?" if sugg else None
                }

            if "FROM" not in self.query.upper():
                return {
                    "error": "Missing FROM keyword.",
                    "suggestion": "Format: DELETE FROM <table_name> [WHERE <condition>]"
                }

            if self.query.upper().startswith("DELETE") and not re.search(
                r"DELETE\s+FROM", self.query, re.IGNORECASE
            ):
                return {
                    "error": "Invalid DELETE syntax.",
                    "suggestion": "Did you forget the FROM keyword?"
                }

            return {
                "error": "Invalid DELETE syntax.",
                "suggestion": "Format: DELETE FROM <table_name> [WHERE <condition>]"
            }

        self.table_name = match.group(1)
        where_clause = match.group(2)

        if self.table_name.upper() in {
            "DELETE", "FROM", "WHERE", "SELECT",
            "INSERT", "UPDATE", "TABLE", "DATABASE"
        }:
            return {
                "error": "Invalid table name.",
                "suggestion": f"Choose a different name than '{self.table_name}'."
            }

        if where_clause is not None:
            result = self._validate_where_clause(where_clause)
            if result:
                return result

        return None

    def _validate_where_clause(self, where_clause):
        where_clause = where_clause.strip()

        if where_clause.endswith(";"):
            where_clause = where_clause[:-1].strip()

        if not where_clause:
            return {
                "error": "Empty WHERE clause.",
                "suggestion": "Specify a condition after WHERE."
            }

        return None

