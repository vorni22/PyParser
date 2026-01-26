from .Lexer import Lexer
from .Grammar import Grammar

class Parser():
    def __init__(self, lexer: Lexer, grammar: Grammar) -> None:
        self.lexer = lexer
        self.grammar = grammar

    
    def parse(self, input: str) -> str:
        # lex the input
        tokens = self.lexer.lex(input)

        # check for errors
        if tokens and tokens[0][0] == "":
            return tokens[0][1]

        # filter out spaces
        tokens = [token for token in tokens if token[0] != "SPACE"]

        # parse the tokens
        P = self.grammar.cykParse(tokens)

        if P:
            return str(P)
        
        return "Error lol"
