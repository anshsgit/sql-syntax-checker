from commit_checker import CommitChecker
from rollback_checker import RollbackChecker
from savepoint_checker import SavepointChecker


class TCLValidator:
    """
    Routes SQL queries to appropriate TCL checkers.
    """

    def __init__(self):
        self.commit_checker = CommitChecker()
        self.rollback_checker = RollbackChecker()
        self.savepoint_checker = SavepointChecker()

    def validate(self, query: str):
        for checker in [
            self.commit_checker,
            self.rollback_checker,
            self.savepoint_checker
        ]:
            result = checker.validate(query)
            if result:
                return result

        return {
            "valid": False,
            "error": "Unsupported TCL statement.",
            "reason": "Only COMMIT, ROLLBACK, and SAVEPOINT are supported."
        }
