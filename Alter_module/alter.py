import re
import sys
import os

# # Add the parent directory (root) to sys.path to verify imports work
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

    def analyse(self):
        match = self.alter_pattern.match(self.query)

        if not match:
            first_words = self.query.split(maxsplit=2)

            if len(first_words) > 0 and first_words[0].upper() != "ALTER":
                suggestions = SpellChecker.check(first_words[0])
                if suggestions:
                    return {
                        "error": "Query must start with 'ALTER TABLE'.",
                        "suggestion": f"Did you mean '{suggestions[0]}'?"
                    }

            if len(first_words) > 1 and first_words[1].upper() != "TABLE":
                suggestions = SpellChecker.check(first_words[1])
                if suggestions:
                    return {
                        "error": "Query must start with 'ALTER TABLE'.",
                        "suggestion": f"Did you mean '{suggestions[0]}'?"
                    }

            return {
                "error": "Invalid ALTER TABLE syntax.",
                "suggestion": "Format: ALTER TABLE <table_name> <action> ..."
            }

        self.table_name = match.group(1)
        remaining_query = match.group(2).strip()

        if self.table_name.upper() in [
            "ADD", "DROP", "MODIFY", "ALTER", "TABLE",
            "COLUMN", "CREATE", "INSERT", "UPDATE",
            "DELETE", "SELECT"
        ]:
            return {
                "error": "Invalid or missing table name.",
                "suggestion": "Format: ALTER TABLE <table_name> <action> ..."
            }

        if not remaining_query or remaining_query == ";":
            return {
                "error": "No actions specified for ALTER TABLE.",
                "suggestion": "Specify an action like ADD, DROP, or MODIFY."
            }

        return self._process_commands(remaining_query)


    def _process_commands(self, commands_str):
        if commands_str.endswith(";"):
            commands_str = commands_str[:-1]

        commands = re.findall(r'(?:[^,()]|\([^()]*\))+', commands_str)
        commands = [cmd.strip() for cmd in commands if cmd.strip()]

        for cmd in commands:
            result = self._validate_single_command(cmd)
            if result:
                return result

        return None

    def _validate_single_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return None

        verb = parts[0].upper()

        if verb == "ADD":
            return self._handle_add(parts)
        elif verb == "DROP":
            return self._handle_drop(parts)
        elif verb == "MODIFY":
            return self._handle_modify(parts)
        elif verb == "ALTER":
            return {
                "error": f"Unsupported sub-command '{verb}'.",
                "suggestion": "Use MODIFY COLUMN instead of ALTER COLUMN."
            }
        else:
            suggestions = SpellChecker.check(verb)
            return {
                "error": f"Unknown sub-command '{verb}'.",
                "suggestion": f"Did you mean '{suggestions[0]}'?" if suggestions else None
            }
        
    def _handle_add(self, parts):
        idx = 2 if len(parts) > 1 and parts[1].upper() == "COLUMN" else 1

        if len(parts) < idx + 2:
            return {
                "error": "Incomplete ADD command.",
                "suggestion": "Format: ADD (COLUMN) <column_name> <data_type>"
            }

        col_name = parts[idx]
        data_type = " ".join(parts[idx + 1:])

        return self._validate_type(data_type, col_name)



    def _handle_drop(self, parts):
        idx = 1
        if len(parts) > 1:
            if parts[1].upper() == "COLUMN":
                idx = 2
            else:
                sugg = SpellChecker.check(parts[1])
                if sugg and sugg[0] == "COLUMN":
                    return {
                        "error": "Invalid DROP syntax.",
                        "suggestion": f"Did you mean 'COLUMN' instead of '{parts[1]}'?"
                    }

        if len(parts) < idx + 1:
            return {
                "error": "Incomplete DROP command.",
                "suggestion": "Format: DROP COLUMN <column_name>"
            }

        if len(parts) > idx + 1:
            return {
                "error": "Too many arguments for DROP command.",
                "suggestion": f"Did you mean: DROP COLUMN {parts[idx]}?"
            }

        return None

    def _handle_modify(self, parts):
        idx = 1
        if len(parts) > 1:
            if parts[1].upper() == "COLUMN":
                idx = 2
            else:
                sugg = SpellChecker.check(parts[1])
                if sugg and sugg[0] == "COLUMN":
                    return {
                        "error": "Invalid MODIFY syntax.",
                        "suggestion": f"Did you mean 'COLUMN' instead of '{parts[1]}'?"
                    }

        if len(parts) < idx + 2:
            return {
                "error": "Incomplete MODIFY command.",
                "suggestion": "Format: MODIFY (COLUMN) <column_name> <data_type>"
            }

        col_name = parts[idx]
        data_type = " ".join(parts[idx + 1:])

        return self._validate_type(data_type, col_name)


    def _handle_alter_column(self, parts):
        idx = 1
        if len(parts) > 1 and parts[1].upper() == "COLUMN":
            idx = 2

        if len(parts) < idx + 1:
            return {
                "error": "Incomplete ALTER command.",
                "suggestion": "Use: MODIFY COLUMN <column_name> <data_type>"
            }

        return {
            "error": "ALTER COLUMN is not supported.",
            "suggestion": "Use MODIFY COLUMN for ANSI/MySQL compatibility."
        }


    def _validate_type(self, data_type, col_name):
        base_type = data_type.split()[0]

        if not self.type_pattern.match(base_type):
            suggestions = SpellChecker.check(base_type)
            return {
                "error": f"Invalid data type '{base_type}' for column '{col_name}'.",
                "suggestion": f"Did you mean '{suggestions[0]}'?" if suggestions else None
            }

        return None

