import difflib

class SpellChecker:
    """
    A utility class to suggest corrections for misspelled SQL keywords.
    """
    
    KEYWORDS = [
        "ALTER", "TABLE", "ADD", "DROP", "MODIFY", "COLUMN",
        "INT", "INTEGER", "VARCHAR", "CHAR", "TEXT", "DATE", 
        "DATETIME", "DECIMAL", "FLOAT", "BOOLEAN", "SELECT", 
        "INSERT", "UPDATE", "DELETE", "FROM", "WHERE", "AND", "OR"
    ]

    @staticmethod
    def check(word):
        """
        Checks if a word is a valid keyword. If not, returns suggestions.
        
        Args:
            word (str): The word to check.
            
        Returns:
            list: A list of suggested corrections if the word is close to a keyword.
        """
        word_upper = word.upper()
        if word_upper in SpellChecker.KEYWORDS:
            return []
            
        # Get close matches (cutoff=0.6 means 60% similarity required)
        matches = difflib.get_close_matches(word_upper, SpellChecker.KEYWORDS, n=3, cutoff=0.6)
        return matches
