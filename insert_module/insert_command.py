from insert_module.insert_parser import InsertParser
from insert_module.insert_validator import InsertValidator

class InsertCommand:
    """
    Single entry point for INSERT validation.
    """

    def __init__(self):
        self.parser = InsertParser()
        self.validator = InsertValidator()

    def validate(self, query: str):
        parsed = self.parser.parse_insert(query)
        return self.validator.validate_insert(parsed)
