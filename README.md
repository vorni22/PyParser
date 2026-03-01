# Parser

A from-scratch implementation of a **lexer** and **parser** pipeline in Python, covering the full chain from regular expressions to parse trees. No external parsing libraries are used — every component (regex engine, NFA, DFA, lexer, grammar, CYK parser) is built from first principles.

## Overview

The project implements a complete text-processing pipeline:

```
Input string
  → Lexer (regex-based tokenization)
    → Token stream
      → Parser (CYK algorithm on a CNF grammar)
        → Parse tree
```

## Components

| Module | Description |
|---|---|
| **Regex** | Tokenizes, desugars (e.g. `[a-z]`), and converts regular expressions to postfix notation, then builds NFAs via Thompson's construction. |
| **NFA** | Non-deterministic finite automaton with epsilon transitions. Supports epsilon-closure computation and subset construction to convert to a DFA. |
| **DFA** | Deterministic finite automaton with word acceptance and Hopcroft's algorithm for state minimization. |
| **Lexer** | Takes a list of `(token_name, regex)` pairs, builds a combined NFA/DFA, and performs longest-match tokenization with priority based on spec order. |
| **Grammar** | Reads a context-free grammar in Chomsky Normal Form from a file and implements the CYK parsing algorithm. |
| **Parser** | Orchestrates the lexer and grammar — lexes the input, filters whitespace, runs CYK, and returns the parse tree. |
| **ParseTree** | Tree data structure for representing parse results with pretty-printed indented output. |

## Usage

### 1. Define a lexer specification

Create a JSON file mapping token names to regular expressions:

```json
{
    "LAMBDA": "\\\\",
    "LPAREN": "\\(",
    "RPAREN": "\\)",
    "POINT": "\\.",
    "VAR": "[a-z]",
    "OP": "(\\+|\\-|\\*|/)",
    "SPACE": "(\\ |\\n|\\t|\\r)+",
    "NUMBER": "[0-9]+"
}
```

Supported regex syntax: literals, `|` (union), `*` (Kleene star), `+` (one or more), `?` (optional), `()` (grouping), `[a-z]` (character ranges), `\\` (escape).

### 2. Define a grammar in Chomsky Normal Form

Create a text file where each line is a production rule. Binary rules use a space-separated right-hand side; unary rules map a non-terminal to a terminal. The first non-terminal listed becomes the start symbol.

```
expr: int_2 expr
expr: int_3 int_rparen
expr: int_4 expr
expr: VAR
expr: NUMBER
int_1: int_lambda int_var
int_2: int_1 int_point
int_3: int_lparen expr
int_4: expr int_op
int_lambda: LAMBDA
int_var: VAR
int_point: POINT
int_lparen: LPAREN
int_rparen: RPAREN
int_op: OP
```

Intermediate non-terminals (prefixed with `int_`) are used to encode the original grammar in CNF. They are collapsed during parse tree output.

### 3. Parse an input string

```python
from src.Parser import Parser
from src.Lexer import Lexer
from src.Grammar import Grammar
import json

# Load lexer spec
with open("lexer_spec.json") as f:
    spec = list(json.load(f).items())

lexer = Lexer(spec)
grammar = Grammar.fromFile("grammar_lambda.txt")
parser = Parser(lexer, grammar)

result = parser.parse("(a + b)")
print(result)
```

Output:

```
expr
  (LPAREN: ()
  expr
    (VAR: a)
    (OP: +)
    (VAR: b)
  (RPAREN: ))
```

### Using individual components

**Regex → NFA → DFA:**

```python
from src.Regex import parse_regex

regex = parse_regex("[a-z]+")
nfa = regex.thompson()
dfa = nfa.subset_construction()
print(dfa.accept("hello"))   # True
print(dfa.accept("hello1"))  # False
```

**Lexer only:**

```python
from src.Lexer import Lexer

spec = [("NUMBER", "[0-9]+"), ("PLUS", "\\+"), ("SPACE", "\\ +")]
lexer = Lexer(spec)
print(lexer.lex("12 + 34"))
# [('NUMBER', '12'), ('SPACE', ' '), ('PLUS', '+'), ('SPACE', ' '), ('NUMBER', '34')]
```

**DFA minimization:**

```python
min_dfa = dfa.minimize()
```

## How It Works

### Regex → NFA (Thompson's Construction)

1. The regex string is **tokenized** into characters and operators.
2. **Syntactic sugar** like `[a-z]` is expanded into union expressions `(a|b|...|z)`.
3. Implicit **concatenation operators** (`.`) are inserted between adjacent tokens where needed.
4. The token list is converted to **postfix (reverse Polish) notation** using the shunting-yard algorithm with operator precedence: `* + ?` > `.` > `|`.
5. The postfix tokens are evaluated with a stack to build an NFA via **Thompson's construction**, where each operator (character, concatenation, union, star, plus, optional) produces a small NFA fragment that is composed together.

### NFA → DFA (Subset Construction)

The NFA is converted to an equivalent DFA using the **subset construction** (powerset construction) algorithm. Each DFA state represents a set of NFA states. Epsilon closures are precomputed and cached for efficiency.

### DFA Minimization (Hopcroft's Algorithm)

The DFA can be minimized using **Hopcroft's partition-refinement algorithm**, which merges indistinguishable states to produce the smallest equivalent DFA.

### Lexer (Longest Match)

Multiple token regexes are compiled into individual NFAs, linked to a shared start state via epsilon transitions, and converted into a single combined DFA. During tokenization, the lexer uses **longest-match semantics** — it advances through the DFA as far as possible, and when no further transition exists, emits the token corresponding to the last accepting state. Token priority is determined by **specification order** (earlier entries win on ties).

### Parser (CYK Algorithm)

The **Cocke–Younger–Kasami (CYK)** algorithm is used for parsing. It requires the grammar to be in **Chomsky Normal Form** (every production is either `A → BC` or `A → a`). The algorithm fills a dynamic programming table `dp[i][j]` representing all non-terminals that can derive the substring of length `j` starting at position `i`. Parse trees are constructed alongside the DP computation.

## Running Tests

```bash
python -m pytest test/
```

## Project Structure

```
src/
  Regex.py      – Regex parsing and Thompson's construction
  NFA.py        – NFA with epsilon closure and subset construction
  DFA.py        – DFA with acceptance and Hopcroft minimization
  Lexer.py      – Regex-based tokenizer
  Grammar.py    – CNF grammar and CYK parser
  Parser.py     – Combined lexer + parser pipeline
  ParseTree.py  – Parse tree representation

tests_1/        – DFA test cases
tests_2/        – Regex/NFA test cases
tests_4/        – Parser/grammar test cases
test/           – Unit test suites
```

## Requirements

- Python 3.12+ (uses `class DFA[STATE]` PEP 695 syntax for generic types)
- No external dependencies
