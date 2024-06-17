import sys
import json
from graphviz import Digraph

ALLOWED = "0123456789qwertyuiopasdfghjklzxcvbnm*.+()$"
OPS = "*.+()"
PRIORITY = {'*': 2, '.': 1, '+': 0}
INVALID_REGEX = -1
VALID_REGEX = 0

class State:
    id = 0

    def __init__(self):
        self.id = State.id
        self.name = ""
        State.id += 1
        self.transitions = []

    def addTransition(self, node, alph):
        self.transitions.append((node, alph))

class NFA:
    def __init__(self):
        self.states = []
        self.start = None
        self.accept = []
        self.alphabet = []

    def getAlph(self, regex):
        for c in regex:
            if c not in OPS and c not in self.alphabet:
                self.alphabet.append(c)

    def getStart(self):
        return self.start

    def getAccept(self):
        return self.accept

    def addState(self, s):
        self.states.append(s)

    def addTransition(self, s1, s2, a):
        s1.addTransition(s2, a)

    def makeStart(self, s):
        self.start = s

    def makeAccept(self, s):
        self.accept.append(s)

    def removeAccept(self, s):
        self.accept.remove(s)

    def names(self):
        c = 0
        self.start.name = f"q{c}"
        c += 1
        states = [self.start]
        while states:
            cur = states.pop(0)
            for state, alph in cur.transitions:
                if not state.name:
                    state.name = f"q{c}"
                    c += 1
                    states.append(state)

    def printTuple(self, path):
        js = {
            'states': [state.name for state in self.states],
            'letters': self.alphabet,
            'transition_function': [
                [state.name, alph, node.name]
                for state in self.states
                for node, alph in state.transitions
            ],
            'start_states': [self.start.name],
            'final_states': [state.name for state in self.accept]
        }
        with open(path, 'w') as f:
            json.dump(js, f, indent=4)

def addConcat(regEx):
    res = []
    for i in range(len(regEx)):
        res.append(regEx[i])
        if regEx[i] not in '(.+':
            if i + 1 < len(regEx) and regEx[i + 1] not in ')*+.':
                res.append('.')
    return "".join(res)

def parseRegEx(regEx, postfix):
    # Eliminar espacios en blanco de la expresión regular
    regEx = regEx.replace(" ", "")

    if regEx == "":
        return VALID_REGEX

    for a in regEx:
        if a not in ALLOWED:
            return INVALID_REGEX

    postfix.clear()
    stack = []
    for a in regEx:
        if a not in OPS:
            postfix.append(a)
        elif a == '(':
            stack.append('(')
        elif a == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(' and PRIORITY[a] <= PRIORITY[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(a)
    while stack:
        postfix.append(stack.pop())
    return VALID_REGEX


def readJSON(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data.get('regex', '')

def visualize_nfa(nfa_json, output_path):
    dot = Digraph()
    for state in nfa_json["states"]:
        if state in nfa_json["final_states"]:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)
    for transition in nfa_json["transition_function"]:
        start_state, symbol, end_state = transition
        if symbol == "$":
            label = "ε"
        else:
            label = symbol
        dot.edge(start_state, end_state, label=label)
    for start_state in nfa_json["start_states"]:
        dot.node("start", shape="point")
        dot.edge("start", start_state)
    dot.render(output_path, format='png', cleanup=True)

def kleene_base_cases(symbol):
    if symbol == '$':
        nfa = NFA()
        start_state = State()
        nfa.addState(start_state)
        nfa.makeStart(start_state)
        nfa.makeAccept(start_state)
        return nfa
    elif symbol == 'p':
        nfa = NFA()
        start_state = State()
        nfa.addState(start_state)
        nfa.makeStart(start_state)
        return nfa
    else:
        nfa = NFA()
        q0 = State()
        nfa.addState(q0)
        nfa.makeStart(q0)
        q1 = State()
        nfa.addState(q1)
        nfa.makeAccept(q1)
        nfa.addTransition(q0, q1, symbol)
        return nfa






def kleene_union(nfa1, nfa2):
    nfa = NFA()
    start = State()
    nfa.addState(start)
    nfa.makeStart(start)
    nfa.addTransition(start, nfa1.start, '$')
    nfa.addTransition(start, nfa2.start, '$')
    nfa.states += nfa1.states + nfa2.states
    nfa.accept = nfa1.accept + nfa2.accept
    return nfa

def kleene_concat(nfa1, nfa2):
    nfa = NFA()
    nfa.states = nfa1.states + nfa2.states
    nfa.start = nfa1.start
    nfa.accept = nfa2.accept
    for accept_state in nfa1.accept:
        accept_state.addTransition(nfa2.start, '$')
        nfa1.removeAccept(accept_state)
    return nfa

def kleene_star(nfa1):
    nfa = NFA()
    start = State()
    nfa.addState(start)
    nfa.makeStart(start)
    nfa.addTransition(start, nfa1.start, '$')
    for accept_state in nfa1.accept:
        nfa.addTransition(accept_state, nfa1.start, '$')
        nfa.addTransition(accept_state, start, '$')
    nfa.states += nfa1.states
    nfa.accept.append(start)
    return nfa

def thompson(regEx):
    postfix = []
    if parseRegEx(addConcat(regEx), postfix) == INVALID_REGEX:
        raise ValueError("Invalid regular expression")

    if not postfix:
        nfa = NFA()
        start_state = State()
        nfa.addState(start_state)
        nfa.makeStart(start_state)
        nfa.makeAccept(start_state)
        return nfa

    stackNFA = []
    for symbol in postfix:
        if symbol not in OPS:
            stackNFA.append(kleene_base_cases(symbol))
        elif symbol == '+':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            stackNFA.append(kleene_union(N1, N2))
        elif symbol == '.':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            stackNFA.append(kleene_concat(N1, N2))
        elif symbol == '*':
            N = stackNFA.pop()
            stackNFA.append(kleene_star(N))

    if not stackNFA:
        raise ValueError("Invalid regular expression")

    return stackNFA[0]

def main():
    if len(sys.argv) != 3:
        print("Usage: python regex-NFA.py <input_json> <output_json>")
        exit()

    regEx = readJSON(sys.argv[1])
    if not regEx:
        regEx = ""

    nfa = thompson(regEx)
    nfa.getAlph(regEx)
    nfa.names()
    output_path = sys.argv[2]
    nfa.printTuple(output_path)

    with open(output_path, 'r') as f:
        nfa_json = json.load(f)
    visualize_nfa(nfa_json, output_path.replace('.json', ''))

if __name__ == "__main__":
    main()
