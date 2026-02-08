from tcl.commit_checker import CommitChecker
from tcl.rollback_checker import RollbackChecker
from tcl.savepoint_checker import SavepointChecker


class TCLValidator:
    def __init__(self):
        self.checkers = [
            CommitChecker(),
            RollbackChecker(),
            SavepointChecker()
        ]

    def validate(self, query: str):
        if not query or not query.strip():
            return None

        upper = query.strip().upper()

        for checker in self.checkers:
            result = checker.validate(query)

            # If checker applies and finds an error
            if result is not None:
                return result

            # If checker applies and is valid → stop
            if upper.startswith(
                ("COMMIT", "ROLLBACK", "SAVEPOINT")
            ):
                return None

        return {
            "error": "Unsupported TCL statement.",
            "suggestion": "Use COMMIT;, ROLLBACK;, ROLLBACK TO <savepoint>, or SAVEPOINT <name>;"
        }
