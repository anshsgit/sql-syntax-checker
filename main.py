from QueryParser import QueryParser


q = input("Enter your query: ")
parser = QueryParser(q)
print(parser.analyse())