from .ParseTree import ParseTree
from collections import defaultdict

EPSILON = ""

class Grammar:

    @classmethod
    def fromFile(cls, file_name: str):
        with open(file_name, 'r') as f:
            V = set()
            R = set()
            S = None
            line = f.readline().strip()
            while line:
                v, rest = line.split(": ")
                V.add(v)
                if not S:
                    S = v

                alternatives = rest.split("|")
                for alt in alternatives:
                    if " " in alt:
                        n1, n2 = alt.split(" ")
                        V.add(n1)
                        V.add(n2)
                        R.add((v, n1, n2))
                    else: 
                        V.add(alt)
                        R.add((v, alt, None))
            
                line = f.readline().strip()

        return cls(V, R, S)
    
    def __init__(self, V: set[str], R: set[tuple[str, str, str|None]], S: str):
        self.V = V # the set of non-terminals and terminals
        self.R = R # the rules (in CNF)
        self.S = S # the start symbol
        
    def cykParse(self, w: list[tuple[str, str]]):
        n = len(w)

        # ALGORITHM DETAILS:
        # dp[i][j] = {(non-terminal X, parse tree P)}, i=0..n-1, j=1..n
        # dp[i][j] := non-terminals X that produce the substring w[i...i+j-1]
        # (starting at i, taking j characters), together with the associated parse tree P
        # general: dp[i][j] = {(X, P) | X => w[i...i+j-1], P is the associated parse tree}

        # initialization: dp[i][1] = {(X, terminal P(w[i]))  | X <- terminal, terminal = w[i]}

        # Rule used for computation:
        # dp[i][j] = {(X, P(name: X, left, right)) | X <- YZ,
        # Y => w[i...i+k-1], Z=>[i+k...i+j-1], k=1...j-1}, equivalently
        # dp[i][j] = {(X, P(name: X, left = dp[i][k].P,
        # right = dp[i+k][j-k].P)) | X <- YZ,
        # Y in dp[i][k].non-terminals,
        # Z in dp[i+k][j-k].non-terminals, k=1...j-1}
        # i=[0...n-j],  j=[2..n],  k=[1...j-1]
        

        # Pre-processing: For each relation of the form X <- YZ,
        # we store a link of the form binary_index[(Y, Z)] -> X
        # i.e. binary_index[(Y, Z)] = {X | X <- YZ}

        binary_index = defaultdict(set)
        for X, Y, Z in self.R:
            if Z is not None:
                binary_index[((Y, Z))].add(X)

        # dp computation:
        dp = [[dict() for _ in range(n + 1)] for _ in range(n)]

        # STEP 1: dp[i][1] = {(X, terminal P(w[i]))  | X <- terminal, terminal = w[i]}
        for i in range(n):
            token, lexeme = w[i]
            for X, Y, Z in self.R:
                if Z is None and Y == token:
                    P = ParseTree(X, (token, lexeme))
                    dp[i][1][X] = P

        # STEP 2:
        # dp[i][j] = {(X, P(name: X, left = dp[i][k].P,
        # right = dp[i+k][j-k].P)) | X <- YZ,
        # Y in dp[i][k].non-terminals,
        # Z in dp[i+k][j-k].non-terminals, k=1...j-1}

        for j in range(2, n + 1):
            for i in range(0, n - j + 1):
                for k in range(1, j):
                    # check all rules X <- YZ where Y is in dp[i][k]
                    # and Z is in dp[i+k][j-k]
                    for Y in dp[i][k]:
                        for Z in dp[i+k][j-k]:
                            for X in binary_index[((Y, Z))]:
                                leftP = dp[i][k][Y]
                                rightP = dp[i + k][j - k][Z]

                                P = ParseTree(X)
                                P.add_children(leftP)
                                P.add_children(rightP)

                                dp[i][j][X] = P

        if self.S in dp[0][n]:
            return dp[0][n][self.S]
        
        return None
