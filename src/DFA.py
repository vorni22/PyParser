from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from typing import TypeVar
from functools import reduce
from collections import defaultdict

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        initial_state = self.q0

        for ch in word:
            if not (initial_state, ch) in self.d:
                print("early exit at ", (initial_state, ch))
                return False
            initial_state = self.d[(initial_state, ch)]

        return initial_state in self.F

    def minimize(self) -> 'DFA[STATE]':
        # Hopcroft's algorithm, source: https://en.wikipedia.org/wiki/DFA_minimization

        acc = frozenset(self.F)
        other = frozenset(self.K - self.F)

        P = set()
        W = set()

        if acc:
            P.add(acc)
            W.add(acc)

        if other:
            P.add(other)
            W.add(other)

        # Inverse the DFA function and store it in pred
        pred = defaultdict(list)
        for (state, ch), next_state in self.d.items():
            pred[(next_state, ch)].append(state)

        # as long as W is not empty
        while W:
            # Wikipedia: choose and remove a set A from W
            A = W.pop()

            for c in self.S:
                # Wikipedia: let X be the set of states for which a transition on c leads to a state in A
                X = {v for u in A for v in pred.get((u, c), [])}

                # Wikipedia: for each set Y in P for which X ∩ Y is nonempty and Y \ X is nonempty do
                selected = {Y: (frozenset(X & Y), frozenset(Y - X)) for Y in P if X & Y and Y - X}
                for Y, (intersection, difference) in selected.items():
                    # remove Y from P and add back the intersection and difference
                    P.remove(Y)
                    if intersection:
                        P.add(intersection)
                    if difference:
                        P.add(difference)

                    # Wikipedia: if Y is in W replace Y in W by the same two sets
                    if Y in W:
                        W.remove(Y)
                        if intersection:
                            W.add(intersection)
                        if difference:
                            W.add(difference)
                    else:
                        # Wikipedia: if |X ∩ Y| <= |Y \ X| then add X ∩ Y to W, else add Y \ X to W
                        if intersection and difference:
                            if len(intersection) <= len(difference):
                                W.add(intersection)
                            else:
                                W.add(difference)
                        elif intersection:
                            W.add(intersection)
                        elif difference:
                            W.add(difference)

        # now P is a set of partitions, each partition representing a state in the minDFA
        # let's name every partition by one of the old states in it

        # for every partition chose a representative state and mark every
        # state in the partition as being a child of the chosen state.
        parent_state = {q : next(iter(U)) for U in P for q in U}

        # compute the set of states and the transition function for the minDFA
        new_K = set()
        new_F = set()
        new_d = {}
        new_q0 = None

        for U in P:
            # name of new state U
            state_name = parent_state[next(iter(U))]

            new_K.add(state_name)
            for q in U:
                if q in self.F:
                    new_F.add(state_name)

                if q is self.q0:
                    new_q0 = state_name
                
                # tranzitions on each character
                for c in self.S:
                    new_d[(state_name, c)] = parent_state[self.d[(q, c)]]

        if new_q0 is None:
            return None

        return DFA[STATE](self.S, new_K, new_q0, new_d, new_F)
        
    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        return self
    
    