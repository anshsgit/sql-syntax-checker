import re
import sys
import os

# Add the parent directory (root) to sys.path to verify imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spell_checker.utils import SpellChecker

class AlterCommand:
    """
    Handles parsing and validation of SQL ALTER TABLE commands.
    
    This class is responsible for:
    1. Validating the basic structure of an ALTER TABLE command.
    2. Parsing multiple sub-commands (ADD, DROP, MODIFY) within a single statement.
    3. Validating column definitions and types.
    4. Providing meaningful error messages and suggestions.
    """

    def __init__(self, query):
        """
        Initializes the AlterCommand with the query string.
        
        Args:
            query (str): The SQL query string to be processed.
        """
        self.query = query.strip()
        self.errors = []
        self.suggestions = []
        self.table_name = None
        # Basic regex to identify ALTER TABLE statements
        # Matches: ALTER TABLE <table_name> <commands>
        self.alter_pattern = re.compile(r"^ALTER\s+TABLE\s+(\w+)\s+(.+)$", re.IGNORECASE | re.DOTALL)
        
        # Regex for supported data types (simplified for this exercise)
        # Matches types like INT, VARCHAR(255), DECIMAL(10,2), DATE, etc.
        self.type_pattern = re.compile(r"^(INT|INTEGER|VARCHAR\(\d+\)|CHAR\(\d+\)|TEXT|DATE|DATETIME|DECIMAL(\(\d+,\d+\))?|FLOAT|BOOLEAN)$", re.IGNORECASE)

    def validate(self):
        """
        Validates the ALTER TABLE command.
        
        Returns:
            dict: A dictionary containing:
                - valid (bool): True if the query is valid, False otherwise.
                - errors (list): List of error messages.
                - suggestions (list): List of suggestions for fixing errors.
        """
        match = self.alter_pattern.match(self.query)
        
        if not match:
            # Check for misspelled ALTER or TABLE at the start
            first_words = self.query.split(maxsplit=2)
            if len(first_words) > 0:
                if first_words[0].upper() != "ALTER":
                     suggestions = SpellChecker.check(first_words[0])
                     if suggestions:
                         self.suggestions.append(f"Did you mean '{suggestions[0]}' instead of '{first_words[0]}'?")
            
            if len(first_words) > 1:
                if first_words[1].upper() != "TABLE":
                     suggestions = SpellChecker.check(first_words[1])
                     if suggestions:
                         self.suggestions.append(f"Did you mean '{suggestions[0]}' instead of '{first_words[1]}'?")

            if not re.match(r"^ALTER\s+TABLE", self.query, re.IGNORECASE):
                self.errors.append("Query must start with 'ALTER TABLE'.")
                self.suggestions.append("Ensure the query begins with 'ALTER TABLE <table_name> ...'")
            else:
                self.errors.append("Invalid ALTER TABLE syntax.")
                self.suggestions.append("Format: ALTER TABLE <table_name> <action> ...")
            return {"valid": False, "errors": self.errors, "suggestions": self.suggestions}
        
        self.table_name = match.group(1)
        remaining_query = match.group(2).strip()

        # Check if table name is a keyword (preventing "ALTER TABLE ADD..." from being parsed as table "ADD")
        if self.table_name.upper() in ["ADD", "DROP", "MODIFY", "ALTER", "TABLE", "COLUMN", "CREATE", "INSERT", "UPDATE", "DELETE", "SELECT"]:
             self.errors.append("Invalid ALTER TABLE syntax. Missing or invalid table name.")
             self.suggestions.append("Format: ALTER TABLE <table_name> <action> ...")
             return {"valid": False, "errors": self.errors, "suggestions": self.suggestions}
        
        # Check if the remaining part (commands) is empty or just a semicolon
        if not remaining_query or remaining_query == ';':
             self.errors.append("No actions specified for ALTER TABLE.")
             self.suggestions.append("Specify an action like ADD, DROP, or MODIFY.")
             return {"valid": False, "errors": self.errors, "suggestions": self.suggestions}

        return self._process_commands(remaining_query)

    def _process_commands(self, commands_str):
        """
        Splits and processes multiple commands separated by commas.
        
        Args:
            commands_str (str): The string containing one or more actions.
        """
        # Remove trailing semicolon if present
        if commands_str.endswith(';'):
            commands_str = commands_str[:-1]
            
        # Use regex to split by comma ONLY if not inside parentheses (field numbers like DECIMAL(10,2))
        # Matches sequences of non-comma characters OR parenthesized groups
        # This handles DECIMAL(10,2) correctly by keeping it together
        commands = re.findall(r'(?:[^,()]|\([^()]*\))+', commands_str)
        commands = [cmd.strip() for cmd in commands]
        
        for cmd in commands:
            if not cmd: # Handle empty strings from trailing commas or double commas
                continue
            self._validate_single_command(cmd)
            
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "suggestions": self.suggestions
        }

    def _validate_single_command(self, cmd):
        """
        Validates a single action (ADD, DROP, MODIFY).
        
        Args:
            cmd (str): A single command string (e.g., "ADD column INT").
        """
        # SPLIT into words to identify the verb
        parts = cmd.split()
        if not parts:
            return

        verb = parts[0].upper()
        
        if verb == "ADD":
             self._handle_add(parts)
        elif verb == "DROP":
             self._handle_drop(parts)
        elif verb == "MODIFY":
             self._handle_modify(parts)
        # Handle "RENAME" or "CHANGE" if needed later, but spec validation requested ADD, DROP, MODIFY
        elif verb == "ALTER":
             # Some dialects use ALTER COLUMN, mapping it to modify logic check or error
             self._handle_alter_column(parts)
        else:
             self.errors.append(f"Unknown sub-command '{verb}' in '{cmd}'.")
             
             # Check for typo in the verb
             suggestions = SpellChecker.check(verb)
             if suggestions:
                 self.suggestions.append(f"Did you mean '{suggestions[0]}' instead of '{verb}'?")
             
             self.suggestions.append("Supported sub-commands: ADD, DROP, MODIFY.")

    def _handle_add(self, parts):
        """
        Validates the ADD sub-command.
        Format: ADD [COLUMN] <column_name> <data_type>
        """
        # Can be "ADD column_name type" or "ADD COLUMN column_name type"
        idx = 1
        if len(parts) > 1:
            if parts[1].upper() == "COLUMN":
                idx = 2
            elif parts[1].upper() != "COLUMN":
                 # Check if 'COLUMN' was misspelled
                 sugg = SpellChecker.check(parts[1])
                 if sugg and sugg[0] == "COLUMN":
                     self.suggestions.append(f"Did you mean 'COLUMN' instead of '{parts[1]}'?")

        if len(parts) < idx + 2:
            self.errors.append(f"Incomplete ADD command: '{' '.join(parts)}'.")
            self.suggestions.append("Format: ADD (COLUMN) <column_name> <data_type>")
            return

        col_name = parts[idx]
        data_type = " ".join(parts[idx+1:]) # Join rest as type (e.g., unsigned int)
        
        self._validate_type(data_type, col_name)

    def _handle_drop(self, parts):
        """
        Validates the DROP sub-command.
        Format: DROP [COLUMN] <column_name>
        """
        idx = 1
        if len(parts) > 1:
            if parts[1].upper() == "COLUMN":
                idx = 2
            elif parts[1].upper() != "COLUMN":
                 # Check if 'COLUMN' was misspelled
                 sugg = SpellChecker.check(parts[1])
                 if sugg and sugg[0] == "COLUMN":
                     self.suggestions.append(f"Did you mean 'COLUMN' instead of '{parts[1]}'?")
            
        if len(parts) < idx + 1:
             self.errors.append(f"Incomplete DROP command: '{' '.join(parts)}'.")
             self.suggestions.append("Format: DROP COLUMN <column_name>")
             return
             
        # Check if there are extra tokens (invalid syntax for standard DROP COLUMN)
        if len(parts) > idx + 1:
             self.errors.append(f"Too many arguments for DROP command: '{' '.join(parts)}'.")
             self.suggestions.append(f"Did you mean: DROP COLUMN {parts[idx]}?")

    def _handle_modify(self, parts):
        """
        Validates the MODIFY sub-command.
        Format: MODIFY [COLUMN] <column_name> <data_type>
        """
        idx = 1
        if len(parts) > 1:
            if parts[1].upper() == "COLUMN":
                idx = 2
            elif parts[1].upper() != "COLUMN":
                 # Check if 'COLUMN' was misspelled
                 sugg = SpellChecker.check(parts[1])
                 if sugg and sugg[0] == "COLUMN":
                     self.suggestions.append(f"Did you mean 'COLUMN' instead of '{parts[1]}'?")
            
        if len(parts) < idx + 2:
            self.errors.append(f"Incomplete MODIFY command: '{' '.join(parts)}'.")
            self.suggestions.append("Format: MODIFY (COLUMN) <column_name> <data_type>")
            return

        col_name = parts[idx]
        data_type = " ".join(parts[idx+1:])
        
        self._validate_type(data_type, col_name)

    def _handle_alter_column(self, parts):
        """
        Handles ALTER COLUMN (common in SQL Server/Postgres), treating it similar to MODIFY.
        """
        self.suggestions.append("For ANSI/MySQL compatibility, try using 'MODIFY COLUMN' instead of 'ALTER COLUMN'.")
        idx = 1
        if len(parts) > 1 and parts[1].upper() == "COLUMN":
            idx = 2
        
        if len(parts) < idx + 1:
             self.errors.append(f"Incomplete ALTER command: '{' '.join(parts)}'.")
             return

    def _validate_type(self, data_type, col_name):
        """
        Validates the data type against a regex whitelist.
        """
        # Remove potential constraints like 'NOT NULL', 'DEFAULT' for type checking
        # Simple split to just check the first word as the type keyword
        base_type = data_type.split()[0]
        # Check for size/precision in parens attached to type
        
        if not self.type_pattern.match(base_type):
            self.errors.append(f"Invalid or unsupported data type '{base_type}' for column '{col_name}'.")
            
            # Check for typo in data type
            sugg = SpellChecker.check(base_type)
            if sugg:
                self.suggestions.append(f"Did you mean '{sugg[0]}' instead of '{base_type}'?")
                
            self.suggestions.append("Supported types: INT, VARCHAR(n), DATE, DECIMAL(p,s), etc.")
