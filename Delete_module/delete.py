import re
import sys
import os

# Add the parent directory (root) to sys.path to verify imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spell_checker.utils import SpellChecker

class DeleteCommand:
    """
    Handles parsing and validation of SQL DELETE commands.
    
    This class is responsible for:
    1. Validating the basic structure of a DELETE command.
    2. Validating the FROM clause and table name.
    3. Validating the WHERE clause (optional).
    4. Providing meaningful error messages and suggestions.
    """

    def __init__(self, query):
        """
        Initializes the DeleteCommand with the query string.
        
        Args:
            query (str): The SQL query string to be processed.
        """
        self.query = query.strip()
        self.errors = []
        self.suggestions = []
        self.table_name = None
        # Basic regex to identify DELETE statements
        # Matches: DELETE FROM <table_name> [WHERE <condition>] [;]
        # Group 1: Table Name
        # Group 2: WHERE clause condition (optional, can be empty string if WHERE is present but no condition)
        self.delete_pattern = re.compile(r"^DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s*(.*))?;?$", re.IGNORECASE | re.DOTALL)

    def validate(self):
        """
        Validates the DELETE command.
        
        Returns:
            dict: A dictionary containing:
                - valid (bool): True if the query is valid, False otherwise.
                - errors (list): List of error messages.
                - suggestions (list): List of suggestions for fixing errors.
        """
        # Check for empty query
        if not self.query:
            return {"valid": False, "errors": ["Empty query."], "suggestions": []}

        match = self.delete_pattern.match(self.query)
        
        if not match:
            # specialized checks for common errors
            first_word = self.query.split()[0].upper()
            if first_word != "DELETE":
                suggestions = SpellChecker.check(first_word)
                if suggestions:
                    self.suggestions.append(f"Did you mean '{suggestions[0]}' instead of '{first_word}'?")
                else:
                    self.suggestions.append("Ensure the query starts with 'DELETE'.")
            
            # Check for missing FROM
            if "FROM" not in self.query.upper():
                self.errors.append("Missing 'FROM' keyword.")
                self.suggestions.append("Format: DELETE FROM <table_name> [WHERE <condition>]")
            
            # Check if it starts with DELETE but fails basic pattern (e.g. DELETE table)
            elif self.query.upper().startswith("DELETE") and not re.search(r"DELETE\s+FROM", self.query, re.IGNORECASE):
                 self.errors.append("Invalid DELETE syntax.")
                 self.suggestions.append("Did you forget the 'FROM' keyword? Example: DELETE FROM users ...")

            if not self.errors:
                 self.errors.append("Invalid DELETE syntax.")
                 self.suggestions.append("Format: DELETE FROM <table_name> [WHERE <condition>]")

            return {"valid": False, "errors": self.errors, "suggestions": self.suggestions}
        
        self.table_name = match.group(1)
        where_clause = match.group(2)

        # Check if table name is a keyword
        if self.table_name.upper() in ["DELETE", "FROM", "WHERE", "SELECT", "INSERT", "UPDATE", "TABLE", "DATABASE"]:
             self.errors.append("Invalid table name. Table name cannot be a reserved keyword.")
             self.suggestions.append(f"Choose a different name for the table '{self.table_name}'.")
             return {"valid": False, "errors": self.errors, "suggestions": self.suggestions}
        
        # If WHERE clause exists, perform basic validation
        if where_clause:
            self._validate_where_clause(where_clause)

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "suggestions": self.suggestions
        }

    def _validate_where_clause(self, where_clause):
        """
        Validates the WHERE clause.
        
        Args:
            where_clause (str): The condition string from the WHERE clause.
        """
        where_clause = where_clause.strip()
        
        # Remove trailing semicolon if present (in case regex captured it in group 2)
        if where_clause.endswith(';'):
            where_clause = where_clause[:-1].strip()

        if not where_clause:
            self.errors.append("Empty WHERE clause.")
            self.suggestions.append("Specify a condition for the WHERE clause.")
            return
