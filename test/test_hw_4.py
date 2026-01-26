import unittest
from src.Parser import Parser
from src.Lexer import Lexer
from src.Grammar import Grammar
import json

class HW4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.score = 0

        with open("lexer_spec.json", "r") as f:
            spec = json.load(f)
            spec = list(spec.items())

        lexer = Lexer(spec)
        grammar = Grammar.fromFile("grammar_lambda.txt")
        cls.parser = Parser(lexer, grammar)

    @classmethod
    def tearDownClass(cls):
        print("\nParser - Total score:", cls.score, "/ 25\n")

    def expected_result(self, test_name: str) -> str:
        with open(f"tests_4/{test_name}.ref", "r") as f:
            content = f.read()
            return content
        
    def write_result(self, test_name: str, result: str) -> str:
        with open(f"tests_4/{test_name}.ref", "w") as f:
            f.write(result)
        
    def test_example(self):
        spec = [("TYPE", "Int"),
                ("ID", "[a-z]"),
                ("EQUAL", "="),
                ("NUMBER", "[0-9]+"),
                ("PLUS", "\\+"),
                ("SPACE", "\\ ")]
        lexer = Lexer(spec)
        grammar = Grammar.fromFile("tests_4/grammar_example.txt")
        parser = Parser(lexer, grammar)
        result = parser.parse("Int x = 1 + 2")
        self.assertEqual(result, self.expected_result("test_example"))

    def test_1(self):
        parser = self.parser
        string = "(a + b)"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_1"))
        HW4Test.score += 1
        
    def test_2(self):
        parser = self.parser
        string = "a + (b * c)"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_2"))
        HW4Test.score += 1
        
    def test_3(self):
        parser = self.parser
        string = "(a - b) * (c + d)"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_3"))
        HW4Test.score += 1
		
    def test_4(self):
        parser = self.parser
        string = "(a - 4) - (4 * (c + d))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_4"))
        HW4Test.score += 1
        
    def test_5(self):
        parser = self.parser
        string = "5 + ((x * 3) * (y - ((z * 2) * (x + (y -z)))))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_5"))
        HW4Test.score += 1
        
    def test_6(self):
        parser = self.parser
        string = "\\x.x"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_6"))
        HW4Test.score += 2
    
    def test_7(self):
        parser = self.parser
        string = "\\x.(x + 2)"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_7"))
        HW4Test.score += 2
        
    def test_8(self):
        parser = self.parser
        string = "\\x.(x + (7 * y))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_8"))
        HW4Test.score += 2
    
    def test_9(self):
        parser = self.parser
        string = "\\x.\\y.(x + y)"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_9"))
        HW4Test.score += 2
        
    def test_10(self):
        parser = self.parser
        string = "\\x.\\y.(x + (y / z))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_10"))
        HW4Test.score += 2
        
    def test_11(self):
        parser = self.parser
        string = "\\x.\\y.\\z.(x - (y + z))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_11"))
        HW4Test.score += 2
        
    def test_12(self):
        parser = self.parser
        string = "\\x.\\y.\\z.(7 + ((y * z) + (x - y)))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_12"))
        HW4Test.score += 2
        
    def test_13(self):
        parser = self.parser
        string = "\\x.\\y.\\z.(x + (z * \\x.(x * y)))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_13"))
        HW4Test.score += 3
        
    def test_14(self):
        parser = self.parser
        string = "\\x.\\y.\\z.\\v.(x + (z * \\x.(x * \\y.(y - \\z.(z * \\v.(v + x))))))"
        result = parser.parse(string)
        self.assertEqual(result, self.expected_result("test_14"))
        HW4Test.score += 3
        
    
