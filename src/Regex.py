from typing import Any, List
from .NFA import NFA
from collections import defaultdict
from dataclasses import dataclass
import time

EPSILON = ''

OP = "OP"
CH = "CH"

@dataclass
class StatePair:
    q0: int
    qf: int

@dataclass
class TNode:
    op : str                    # operator: "NO", "*", "+", "?", ".", "|", "(" , ")"
    ch : str                    # character if op == "NO", else empty string
    operants : List['TNode']    # child nodes (operands) for operators

    def __init__(self, op, ch):
        self.op = op
        self.ch = ch
        self.operants = []

class Regex:
    def __init__(self, tokens, S):
        self.tokens = tokens # in reverse Polish notation
        self.S = S

    def thompson(self) -> NFA[int]:
        d = defaultdict(set)
        current = 0
        stack = [] # will store partial NFA-ish data (not an actual NFA, just the start and final state of it)

        for token in self.tokens:
            if token[0] == 'CH':
                op = Character(current, token[1])
                current = op.next_current()
                sp = op.thompson(d)
                stack.append(sp)

            elif token[0] == 'OP':
                if token[1] in '*+?':
                    single = stack.pop()
                    if token[1] == '*':
                        op = Star(current, single)
                    elif token[1] == '+':
                        op = Plus(current, single)
                    elif token[1] == '?':
                        op = QuestionMark(current, single)
                    current = op.next_current()
                    sp = op.thompson(d)
                    stack.append(sp)

                elif token[1] == '.':
                    right = stack.pop()
                    left = stack.pop()
                    op = Concat(current, left, right)
                    current = op.next_current()
                    sp = op.thompson(d)
                    stack.append(sp)

                elif token[1] == '|':
                    right = stack.pop()
                    left = stack.pop()
                    op = Union(current, left, right)
                    current = op.next_current()
                    sp = op.thompson(d)
                    stack.append(sp)

        assert len(stack) == 1, "Stack must contain exactly one NFA at the end"
        sp_final = stack.pop()

        K = range(current)
        F = {sp_final.qf}
        q0 = sp_final.q0

        return NFA[int](self.S, K, q0, d, F)

class RegexOne:
    def __init__(self, current, single : StatePair):
        self.single = single
        self.current = current

class RegexTwo:
    def __init__(self, current, left : StatePair, right : StatePair):
        self.left = left
        self.right = right
        self.current = current

class Character:
    def __init__(self, current, ch):
        self.ch = ch
        self.current = current

    def next_current(self):
        # 2 new states are added
        return self.current + 2

    def thompson(self, d):
        q0 = self.current
        qf = self.current + 1
        d[(q0, self.ch)].add(qf)

        return StatePair(q0, qf)
    
class Concat(RegexTwo):
    def next_current(self):
        # 0 new states are added
        return self.current

    def thompson(self, d):
        q0 = self.left.q0
        qf = self.right.qf
        d[(self.left.qf, EPSILON)].add(self.right.q0)

        return StatePair(q0, qf)

class Union(RegexTwo):
    def next_current(self):
        # 2 new states are added
        return self.current + 2

    def thompson(self, d):
        q0 = self.current
        qf = self.current + 1

        d[(q0, EPSILON)].add(self.left.q0)
        d[(q0, EPSILON)].add(self.right.q0)

        d[(self.left.qf, EPSILON)].add(qf)
        d[(self.right.qf, EPSILON)].add(qf)

        return StatePair(q0, qf)
    
class Plus(RegexOne):
    def next_current(self):
        # 2 new states are added
        return self.current + 2

    def thompson(self, d):
        q0 = self.current
        qf = self.current + 1

        old_qf = self.single.qf

        d[(q0, EPSILON)].add(self.single.q0)
        d[(old_qf, EPSILON)].add(qf)
        d[(old_qf, EPSILON)].add(self.single.q0)

        return StatePair(q0, qf)
    
class QuestionMark(RegexOne):
    def next_current(self):
        # 2 new states are added
        return self.current + 2
    
    def thompson(self, d):
        q0 = self.current
        qf = self.current + 1

        old_qf = self.single.qf

        d[(q0, EPSILON)].add(self.single.q0)
        d[(old_qf, EPSILON)].add(qf)
        d[(q0, EPSILON)].add(qf)

        return StatePair(q0, qf)
    
class Star(RegexOne):
    def next_current(self):
        # 2 new states are added
        return self.current + 2
    
    def thompson(self, d):
        q0 = self.current
        qf = self.current + 1

        old_qf = self.single.qf

        d[(q0, EPSILON)].add(self.single.q0)
        d[(old_qf, EPSILON)].add(qf)
        d[(old_qf, EPSILON)].add(self.single.q0)
        d[(q0, EPSILON)].add(qf)

        return StatePair(q0, qf)

def tokenize(regex : str) -> List[tuple[str, str]]:
    tokens = []
    ops = set("()|*+?[]")
    i = 0
    
    while i < len(regex):
        c = regex[i]

        if c == '\\':
            i += 1
            tokens.append((CH, str(regex[i])))
        elif c in ops:
            tokens.append((OP, str(c)))
        elif c != ' ':
            tokens.append((CH, str(c)))

        i += 1

    return tokens

def replace_syntactic_sugars(tokens : List[tuple[str, str]]) -> List[tuple[str, str]]:
    i = 0
    tokens_out = []

    while i < len(tokens):
        if tokens[i][0] == "OP" and tokens[i][1] == "[":
            # Expect pattern: [ CH - CH ]
            start = tokens[i + 1][1]
            end   = tokens[i + 3][1]

            num_start = ord(start)
            num_end = ord(end)

            # Build sequence: '(' a '|' b '|' ... | 'z' ')'
            sub_seq = [(OP, "(")]
            for c in (chr(j) for j in range(num_start, num_end + 1)):
                sub_seq.append((CH, str(c)))
                if c != end:
                    sub_seq.append((OP, "|"))
            sub_seq.append((OP, ")"))

            tokens_out = tokens_out + sub_seq
            i += 5
        else:
            tokens_out.append(tokens[i])
            i += 1

    return tokens_out

def add_concat_operator(tokens : List[tuple[str, str]]) -> List[tuple[str, str]]:
    proc_tokens = []
    prev = None

    for token in tokens:
        if prev is not None:
            # In order for a '.' operator to be inserted between current token and prev token we need:
            # -> the previous token must be a characher, ') or one of the following operators: '*', '+', '?'
            # -> the current token must be a characher or ')'
            prev_is_good = prev[0] == "CH" or (prev[0] == "OP" and prev[1] == ")")
            prev_is_good_op = prev[0] == "OP" and prev[1] in "*+?"
            cur_is_good = token[0] == "CH" or (token[0] == "OP" and token[1] == "(")

            if cur_is_good and (prev_is_good or prev_is_good_op):
                proc_tokens.append((OP, "."))

        proc_tokens.append(token)
        prev = token

    return proc_tokens

def get_alphabet(tokens : List[tuple[str, str]]) -> List[str]:
    S = set()
    for token in tokens:
        if token[0] == CH:
            S.add(token[1])
    return S

def to_postfix(tokens: list[tuple[str,str]]) -> list[tuple[str,str]]:
    precedence = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
    output = [] # will hold tokens in Reverse Polish notation
    stack = [] # operators inside the same '()' section will always have increasing precedence

    # Algorithm details:
    # if current token is a char: push it to output
    # if current token is '(': push it to the stack
    # if current token is ')': pop from the stack until we find the coresponding (first one found) ')'.
    #                          push to output everything in the order we poped except the ')'
    # if current token is an operator: as long as the top of stack has higher precedence than the current element,
    #                                  pop from the stack and push to the output. at the end push to the stack the operator
    # at the end pop the stack and push to the output

    for token in tokens:
        if token[0] == 'CH':
            output.append(token)
        elif token[0] == 'OP':
            op = token[1]
            if op == '(':
                stack.append(op)
            elif op == ')':
                while stack and stack[-1] != '(':
                    output.append((OP, stack.pop()))
                stack.pop()
            else:
                while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[op]:
                    output.append((OP, stack.pop()))
                stack.append(op)
    
    while stack:
        output.append((OP, stack.pop()))
    
    return output

def parse_regex(regex : str):
    tokens = tokenize(regex)
    tokens = replace_syntactic_sugars(tokens)
    tokens = add_concat_operator(tokens)
    tokens = to_postfix(tokens)
    S = get_alphabet(tokens)
    return Regex(tokens, S)


def time_parse_regex(regex: str):
    timings = {}

    start = time.perf_counter()
    tokens = tokenize(regex)
    timings['tokenize'] = time.perf_counter() - start

    start = time.perf_counter()
    tokens = replace_syntactic_sugars(tokens)
    timings['replace_syntactic_sugars'] = time.perf_counter() - start

    start = time.perf_counter()
    tokens = add_concat_operator(tokens)
    timings['add_concat_operator'] = time.perf_counter() - start

    start = time.perf_counter()
    S = get_alphabet(tokens)
    timings['get_alphabet'] = time.perf_counter() - start

    start = time.perf_counter()
    tokens = to_postfix(tokens)
    timings['to_postfix'] = time.perf_counter() - start

    total_time = sum(timings.values())

    print("Function execution times:")
    for func, t in timings.items():
        print(f"  {func:<25}: {t:.6f} s")
    print(f"  {'total':<25}: {total_time:.6f} s\n")

    return Regex(tokens, S)
