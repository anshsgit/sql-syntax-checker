from select.clauseChecksHelper import extractClauses, checkDuplicateClauses, checkMandatoryClauses, checkOrder
from select.selectChecksHelper import collectQualifiedColumns, checkAggregateFunctions, checkColumnNames, handleSelectOrder, checkStarUsage, extractSelectList, extractAliases
from select.whereChecksHelper import checkParentheses, extractConditions, validateBooleanExpr
from select.fromChecksHelper import validateTableRef, splitRef, extractFromList


class SelectParser:
    def __init__(self):
        self.clauses = []
        self.unresolved_columns = []
        self.from_tables = {}

    def clauseChecks(self, tokens):
        clauses = extractClauses(tokens)
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
    
    def selectChecks(self, tokens):
        
        selectList = extractSelectList(tokens)

        if len(selectList) == 0:
            return {
                "error": "No select statment"
            }
        
        self.unresolved_columns = []

        checks = [checkStarUsage, handleSelectOrder, checkAggregateFunctions, checkColumnNames]
        for check in checks:
            error = check(selectList)
            if error:
                return error
        

        # print("collecting")
        collectQualifiedColumns(selectList, self.unresolved_columns)
        # print("collected")
        return None

    def fromChecks(self, tokens):
        
        fromList = extractFromList(tokens)
        if not fromList:
            return {
                "error": "Table name must be present"
            }
        tableRefs = splitRef(fromList)
        self.from_tables = {}

        for ref in tableRefs:
            res = validateTableRef(ref)
            if "error" in res:
                return res

            alias = res["alias"]
            table = res["table"]

            if alias in self.from_tables:
                return {
                    "error": "Duplicates table alias",
                    "alias": alias
                }
            self.from_tables[alias] = table

        return None
    
    def resolveColumnAliases(self):
        for ref in self.unresolved_columns:
            alias = ref["alias"]

            if alias not in self.from_tables:
                return {
                    "error": "Unknown table alias",
                    "alias": alias,
                    "position": ref["position"]
                }

        return None

                
    def whereChecks(self, tokens):

        if "where" in self.clauses:

            whereTokens = extractConditions(tokens)
            # print(whereTokens)
            isValidParantheses =  checkParentheses(whereTokens)
            if isValidParantheses:
                return isValidParantheses

            return validateBooleanExpr(whereTokens)

        return None
        


    def analyse(self, tokens):
        
        checks = [self.clauseChecks, self.selectChecks, self.fromChecks]
        for check in checks:
            error = check(tokens)
            if error:
                return error
            
        err = self.resolveColumnAliases()
        if err:
            return err
        
        checks = [self.whereChecks]
        for check in checks:
            error = check(tokens)
            if error:
                return error
            

        


        
        return None