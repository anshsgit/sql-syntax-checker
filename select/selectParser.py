from select.clauseChecksHelper import extractClauses, checkDuplicateClauses, checkMandatoryClauses, checkOrder
from select.selectChecksHelper import checkAggregateFunctions, checkColumnNames, handleSelectOrder, checkStarUsage, extractSelectList, extractAliases
from select.whereChecksHelper import checkParentheses, extractConditions, validateBooleanExpr

class SelectParser:
    def __init__(self):
        self.aliases = {}
        self.clauses = []

    def clauseChecks(self, tokens):

        clauses = extractClauses(tokens)
        self.clauses = [clause for clause, _ in clauses]
        checks = [checkDuplicateClauses, checkMandatoryClauses, checkOrder]
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
        
        checks = [checkStarUsage, handleSelectOrder, checkAggregateFunctions, checkColumnNames]
        for check in checks:
            error = check(selectList)
            if error:
                return error
        
        self.aliases = extractAliases(tokens)
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
        
        checks = [self.clauseChecks, self.selectChecks, self.whereChecks]
        for check in checks:
            error = check(tokens)
            if error:
                return error
        
        return None