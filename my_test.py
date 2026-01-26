from src.Regex import Regex, parse_regex
from src.NFA import NFA, EPSILON
from src.DFA import DFA
from src.Lexer import Lexer
from test.test_hw_3 import verify
from functools import reduce
from collections import defaultdict
import unittest
from src.Parser import Parser
from src.Lexer import Lexer
from src.Grammar import Grammar
import json

with open("lexer_spec.json", "r") as f:
    spec = json.load(f)
    spec = list(spec.items())

lexer = Lexer(spec)
grammar = Grammar.fromFile("grammar_lambda.txt")
parser = Parser(lexer, grammar)

string = "(a + b)"
result = parser.parse(string)

print(result)
