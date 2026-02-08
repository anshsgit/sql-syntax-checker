from select.helper.clauseChecksHelper import extractClauses, checkDuplicateClauses, checkMandatoryClauses, checkOrder
from select.helper.selectChecksHelper import collectQualifiedColumns, checkAggregateFunctions, checkColumnNames,containsAggregate, handleSelectOrder, checkStarUsage, extractSelectList, extractAliases
from select.helper.whereChecksHelper import checkParentheses, extractConditions, validateBooleanExpr
from select.helper.fromChecksHelper import validateJoinChain, containsJoin, validateTableRef, splitRef, extractFromList
from select.helper.groupByChecksHelper import normalize, stripAlias, splitGroupByExpressions, validateGroupBy, extractGroupByList, splitSelectExpressions
from select.helper.havingChecksHelper import validateHavingExpr, isValidHavingRHS, stripParens, extractHaving, splitHavingExprs, splitComparison
from select.helper.orderByHelpers import isValidOrderByExpr, splitOrderByItems, extractOrderBy, splitOrderByItems
from select.helper.utils import extractLimit

class SelectParser:
    """
    High-level SQL SELECT statement validator.

    Responsibilities:
    - Enforce clause presence and order
    - Validate SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT
    - Resolve table aliases and column references
    """

    def __init__(self):
        self.clauses = []              # ordered list of clause names
        self.unresolved_columns = []   # qualified columns needing alias resolution
        self.from_tables = {}          # alias -> table mapping

    # ---------------------------------------------------------
    # Clause-level validation
    # ---------------------------------------------------------

    def clauseChecks(self, tokens):
        """
        Validates clause structure:
        - duplicate clauses
        - mandatory clauses
        - clause ordering
        """
        clauses = extractClauses(tokens)
        # print(clauses)
        self.clauses = [name for name, _ in clauses]

        checks = [
            checkDuplicateClauses,
            checkMandatoryClauses,
            checkOrder
        ]

        for check in checks:
            error = check(clauses)
            if error:
                return error

        return None

    # ---------------------------------------------------------
    # SELECT clause validation
    # ---------------------------------------------------------

    def selectChecks(self, tokens):
        """
        Validates SELECT list:
        - structure and ordering
        - aggregate usage
        - column naming
        - star (*) rules
        Also collects qualified columns for later alias resolution.
        """
        selectList = extractSelectList(tokens)

        if len(selectList) == 0:
            return {
                "error": "No select statment"
            }

        self.unresolved_columns = []

        checks = [
            checkStarUsage,
            handleSelectOrder,
            checkAggregateFunctions,
            checkColumnNames
        ]

        for check in checks:
            error = check(selectList)
            if error:
                return error

        # Collect table-qualified column references (table.column)
        collectQualifiedColumns(selectList, self.unresolved_columns)

        return None

    # ---------------------------------------------------------
    # FROM clause validation
    # ---------------------------------------------------------

    def fromChecks(self, tokens):
        """
        Validates FROM clause:
        - normal tables
        - JOIN chains
        - derived tables (subqueries)
        """

        fromList = extractFromList(tokens)
        if not fromList:
            return {
                "error": "Table name must be present"
            }

        self.from_tables = {}

        # --------------------------------------------------
        # JOIN syntax (handled separately)
        # --------------------------------------------------
        if containsJoin(fromList):
            return validateJoinChain(fromList, self)

        # --------------------------------------------------
        # Split comma-separated references (top-level only)
        # --------------------------------------------------
        tableRefs = splitRef(fromList)

        for ref in tableRefs:
            if not ref:
                return {"error": "Empty table reference"}

            # ==================================================
            # 🔥 DERIVED TABLE: (SELECT ...) alias
            # ==================================================
            if ref[0] == "(":

                # must have alias
                if len(ref) < 3 or not ref[-1].isidentifier():
                    return {
                        "error": "Derived table must have an alias"
                    }

                alias = ref[-1]
                inner = stripParens(ref[:-1])

                if not inner or inner[0] != "select":
                    return {
                        "error": "Invalid derived table"
                    }

                from select.selectParser import SelectParser
                parser = SelectParser()
                err = parser.analyse(inner)
                if err:
                    return {
                        "error": "Invalid subquery in FROM",
                        "details": err
                    }

                if alias in self.from_tables:
                    return {
                        "error": "Duplicate table alias",
                        "alias": alias
                    }

                self.from_tables[alias] = "<subquery>"
                continue

            # ==================================================
            # 🔹 NORMAL TABLE
            # ==================================================
            res = validateTableRef(ref)
            if "error" in res:
                return res

            alias = res["alias"]
            table = res["table"]

            if alias in self.from_tables:
                return {
                    "error": "Duplicate table alias",
                    "alias": alias
                }

            self.from_tables[alias] = table

        return None


    # ---------------------------------------------------------
    # Column alias resolution
    # ---------------------------------------------------------

    def resolveColumnAliases(self):
        """
        Ensures all qualified column references refer to known table aliases.
        """
        for ref in self.unresolved_columns:
            alias = ref["alias"]

            if alias not in self.from_tables:
                return {
                    "error": "Unknown table alias",
                    "alias": alias,
                    "position": ref["position"]
                }

        return None

    # ---------------------------------------------------------
    # WHERE clause validation
    # ---------------------------------------------------------


    def whereChecks(self, tokens):
        if "where" in self.clauses:
            whereTokens = extractConditions(tokens)

            err = checkParentheses(whereTokens)
            if err:
                return err

            err = validateBooleanExpr(whereTokens)
            if err:
                return err

            # ✅ NEW: validate qualified column aliases
            unresolved = []
            collectQualifiedColumns(whereTokens, unresolved)

            for ref in unresolved:
                if ref["alias"] not in self.from_tables:
                    return {
                        "error": "Unknown table alias",
                        "alias": ref["alias"],
                        "position": ref["position"]
                    }

        return None

    # ---------------------------------------------------------
    # GROUP BY clause validation
    # ---------------------------------------------------------

    def groupbyChecks(self, tokens):
        """
        Validates GROUP BY clause against SELECT expressions.
        """
        selectList = extractSelectList(tokens)
        selectExprs, err = splitSelectExpressions(selectList)
        if err:
            return err

        # Remove SELECT aliases before comparison
        selectExprs = [stripAlias(expr) for expr in selectExprs]
        has_agg = any(containsAggregate(expr) for expr in selectExprs)
        has_non_agg = any(not containsAggregate(expr) for expr in selectExprs)
        groupTokens = extractGroupByList(tokens)


        if has_agg and has_non_agg and not groupTokens:
            return {
                "error": "GROUP BY is required when mixing aggregate and non-aggregate expressions"
            }
        
        if isinstance(groupTokens, dict):
            return groupTokens
        
        if groupTokens == []:
            return {
                "error": "GROUP BY clause cannot be empty"
            }

        if groupTokens:
            groupExprs, err = splitGroupByExpressions(groupTokens)
            if err:
                return err

            return validateGroupBy(selectExprs, groupExprs)

        return None

    # ---------------------------------------------------------
    # HAVING clause validation
    # ---------------------------------------------------------

    def havingChecks(self, tokens):
        """
        Validates HAVING clause:
        - boolean expression correctness
        - aggregate / GROUP BY compatibility
        """
        if "having" in self.clauses:
            havingTokens = extractHaving(tokens)

            # HAVING must not be empty
            if havingTokens is not None and not havingTokens:
                return {
                    "error": "HAVING clause cannot be empty"
                }

            # Boolean structure validation
            err = validateBooleanExpr(havingTokens, "having")
            if err:
                return {
                    "error": "Invalid HAVING condition",
                    "details": err
                }
            


            # Build GROUP BY normalization set
            groupByTokens = extractGroupByList(tokens)
            groupbyExpr, err = splitGroupByExpressions(groupByTokens)
            if err:
                return err

            group_set = {normalize(expr) for expr in groupbyExpr}

            # Build alias set from SELECT
            selectList = extractSelectList(tokens)
            alias_map = extractAliases(selectList)
            alias_set = set(alias_map.keys())

            return validateHavingExpr(havingTokens, group_set, alias_set)

        return None

    # ---------------------------------------------------------
    # ORDER BY clause validation
    # ---------------------------------------------------------

    def orderByChecks(self, tokens):
        """
        Validates ORDER BY clause:
        - expression resolution
        - alias usage
        - GROUP BY compatibility
        """
        orderTokens = extractOrderBy(tokens)

        if isinstance(orderTokens, dict):
            return orderTokens

        if orderTokens is None:
            return None

        if not orderTokens:
            return {
                "error": "ORDER BY clause cannot be empty"
            }

        # GROUP BY normalization set
        group_set = set()
        groupByTokens = extractGroupByList(tokens)
        if groupByTokens:
            groupbyExpr, err = splitGroupByExpressions(groupByTokens)
            if err:
                return err
            group_set = {normalize(expr) for expr in groupbyExpr}

        # SELECT aliases and expressions
        selectList = extractSelectList(tokens)
        alias_map = extractAliases(selectList)
        alias_set = set(alias_map.keys())

        selectExprs, err = splitSelectExpressions(selectList)
        if err:
            return err
        select_set = {normalize(expr) for expr in selectExprs}

        # Validate each ORDER BY item
        parts = splitOrderByItems(orderTokens)
        for part in parts:
            if not part:
                return {
                    "error": "Invalid ORDER BY expression"
                }

            ok, err = isValidOrderByExpr(
                part,
                select_set,
                alias_set,
                group_set
            )
            if not ok:
                return {
                    "error": err
                }

        return None

    # ---------------------------------------------------------
    # LIMIT clause validation
    # ---------------------------------------------------------

    def limitChecks(self, tokens):
        """
        Validates LIMIT clause:
        - single non-negative integer literal
        """
        limitTokens = extractLimit(tokens)

        if limitTokens is None:
            return None

        if not limitTokens:
            return {"error": "LIMIT clause cannot be empty"}

        if len(limitTokens) != 1:
            return {"error": "LIMIT requires a single integer value"}

        value = limitTokens[0]

        if not value.isdigit():
            return {"error": "LIMIT value must be a non-negative integer"}

        return None

    # ---------------------------------------------------------
    # Full analysis entry point
    # ---------------------------------------------------------

    def analyse(self, tokens):
        """
        Runs all validation phases in correct semantic order.
        Stops on first error.
        """

        # Clause, SELECT, FROM must be validated first
        checks = [
            self.clauseChecks,
            self.selectChecks,
            self.fromChecks
        ]

        for check in checks:
            error = check(tokens)
            if error:
                return error

        # Resolve qualified column references
        err = self.resolveColumnAliases()
        if err:
            return err

        # Remaining clause validations
        checks = [
            self.whereChecks,
            self.groupbyChecks,
            self.havingChecks,
            self.orderByChecks,
            self.limitChecks
        ]

        for check in checks:
            error = check(tokens)
            if error:
                return error

        return None
