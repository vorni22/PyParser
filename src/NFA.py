from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable
from collections import defaultdict

EPSILON = ''

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]


    def epsilon_closure(self, state: STATE) -> set[STATE]:
        closure = {state}
        stack = [state]

        while stack:
            st = stack.pop()

            for t in self.d.get((st, EPSILON), []):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)

        return closure


    # Convert NFA to DFA (subset construction)
    def subset_construction(self) -> DFA[frozenset[STATE]]:
        initial_state = frozenset(self.epsilon_closure(self.q0))

        dfa_k = set()
        dfa_q0 = initial_state
        dfa_d = {}
        dfa_F = set()

        proc = [initial_state]

        # compute the epsilon closure for each state only once and store it
        epsilon_cache = {q: self.epsilon_closure(q) for q in self.K}

        # Continue processing DFA states until none remain unexpanded
        while proc:
            state = proc.pop()
            dfa_k.add(state)

            for c in self.S:
                next_state = set()

                for q in state:
                    if (q, c) in self.d:
                        for ns in self.d[(q, c)]:
                            next_state.update(epsilon_cache[ns])

                next_state = frozenset(next_state)
                dfa_d[(state, c)] = next_state

                if next_state not in dfa_k and next_state not in proc:
                    proc.append(next_state)

        # An DFA state is final iff at least one NFA state in it is final
        dfa_F = {s for s in dfa_k if any(q in self.F for q in s)}

        return DFA[frozenset[STATE]](self.S, dfa_k, dfa_q0, dfa_d, dfa_F)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # apply f on every state lol

        new_K = {f(q) for q in self.K}
        new_q0 = f(self.q0)

        new_d = {}
        for (q, c), targets in self.d.items():
            new_d[(f(q), c)] = {f(t) for t in targets}

        new_F = {f(q) for q in self.F}

        return NFA(
            self.S,
            new_K,
            new_q0,
            new_d,
            new_F
        )
