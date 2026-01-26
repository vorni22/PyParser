from .Regex import Regex, parse_regex
from .NFA import NFA, EPSILON
from .DFA import DFA
from functools import reduce
from collections import defaultdict

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec
        self.tokens = [name for name, _ in spec]
        self.nfa = self.build_combined_nfa(spec)

        # do NOT minimize the resulting dfa since we need to distinguish between final states 
        self.dfa = self.nfa.subset_construction()
    
    def lex(self, word: str) -> list[tuple[str, str]]:
        i = 0
        result = []

        while i < len(word):
            state = self.dfa.q0
            last_accept_state = None
            last_accept_pos = i

            j = i
            line_start = word.rfind('\n', 0, i) + 1

            # The start state is a final state iff one of the regexes was epsilon
            if state in self.dfa.F:
                last_accept_state = state
                last_accept_pos = i

            # advance the dfa as long as there is a transition
            # save the latest state that was final and it's position
            while j < len(word):
                if (state, word[j]) not in self.dfa.d or not self.dfa.d[(state, word[j])]:
                    break
                
                state = self.dfa.d[(state, word[j])]
                j += 1

                if state in self.dfa.F:
                    last_accept_state = state
                    last_accept_pos = j

            # if no state accepts or the only accepting state is the first one (only match is the epsilon regex)
            # than there is an error
            if last_accept_state is None or i == last_accept_pos:
                line_num = word.count('\n', 0, j)
                rel_char_index = j - line_start

                if j < len(word):
                    return [("", f"No viable alternative at character {rel_char_index}, line {line_num}")]
                else:
                    return [("", f"No viable alternative at character EOF, line {line_num}")]

            token_id = self._token_from_dfa_state(last_accept_state)
            token_name = self.tokens[token_id]
            lexeme = word[i:last_accept_pos]

            result.append((token_name, lexeme))
            i = last_accept_pos

        return result

    def build_combined_nfa(self, spec) -> NFA[tuple[int, int | None]]:
        d = defaultdict(set)
        S = set()

        start_state = (0, None)
        next_id = 1

        K = {start_state}
        F = set()

        for token_id, (_, regex) in enumerate(spec):
            r = parse_regex(regex)
            nfa = r.thompson()

            # Map each state to a pair (old state + offset, TOKEN_ID if old_state is final, else None)
            def mapper(q, base=next_id, tid=token_id):
                return (q + base, tid if q in nfa.F else None)

            remapped = nfa.remap_states(mapper)

            # combine the current transition function with the new one
            d[(start_state, EPSILON)].add(remapped.q0)

            for (q, c), targets in remapped.d.items():
                d.setdefault((q, c), set()).update(targets)

            K.update(remapped.K)
            F.update(remapped.F)
            S.update(remapped.S)

            next_id = max(s[0] for s in remapped.K) + 1

        return NFA(
            S,
            K,
            start_state,
            d,
            F
        )
    
    def _token_from_dfa_state(self, state):
        tokens = [tid for (nfa_id, tid) in state if tid is not None]
        return min(tokens) if tokens else None
        


