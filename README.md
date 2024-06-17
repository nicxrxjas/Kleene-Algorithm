# Finite Automata

This repository contains code to convert finite automata to regular expressions, regular expressions to finite automata, NFA's to DFA's and to optimize DFA's.

### How to run

To run any script, simply run the command: `python3 <script-name> <path-to-readfile> <path-to-writefile>`

The files must be in the proper format (examples are provided in the `dumps` folder) and `<path-to-writefile>` does not have to exist.

### Regular expression - NFA

The regular expression to NFA converter works by first parsing the regular expression provided, and converting it into a postfix expression. For example, `a(b*)` will be converted into the expression `ab*.` where `.` represents the concatenation operation.

Once a postfix expression is obtained, the program simply creates an NFA for each character that belongs to the alphabet with one start state and one accept state. If an operation is read, the program works in the following way:

- `.`: Add an epsilon transition from the accept state of the left NFA to the start state of the right NFA and remove these states from the accept/start list respectively.
- `+`: Add a new start state with epsilon transitions to the start states of both NFAs and add a new accept state with epsilon transitions from the original accept states. Remove the original start/accept states from the start/accept lists.
- `*`: Add a new start state and a new accept state with epsilon transitions from the original start and accept states, a transition from the new start state to the new accept state and a transition from the new accept state to the original start state. This is to ensure that the new NFA can also accept an empty string.

![Images/Untitled.png](Images/singleCharacterNFA.png)

An NFA for a single character 'a'.

![Images/Untitled%201.png](Images/concatenationNFA.png)

An NFA for the concatenation of two NFAs. S refers to the start state, I to any intermediate state(s) and A to the accept state. 

![Images/Untitled%202.png](Images/unionNFA.png)

An NFA for the union of two NFAs using the same notation. 

![Images/Untitled%203.png](Images/kleeneNFA.png)

An NFA for the kleene star of an NFA. 

### NFA - DFA

The conversion from an NFA to a DFA is done in the conventional method. We take the powerset of the states of the NFA as the states of the DFA. Now for each transition in the NFA, consider the states in the DFA that contain the NFA state (each DFA state is a set of NFA states) and add transitions to the reachable set of states given the alphabet of the original transition. While performing this operation however, epsilon closure must be taken into account, i.e. the states that are reachable from the state that the automaton transitioned to with epsilon transitions must also be a part of the set of reachable states. 

### DFA - regular expression

To convert a DFA to a regular expression, the finite automaton must first be converted into a generalized NFA. To do this, simply add a new start state and a new accept state where the start state is connected to every other state, and the accept state has incoming transitions from every other state. Now we arbitrarily choose a state to remove ('rip') from the GNFA and modify the rest of the transitions in the automaton using the formula: 

![Images/Untitled%204.png](Images/DFAregex.png)

![Images/Untitled%205.png](Images/DFAregexdesc.png)

If this process is applied on the GNFA until there are only two states left, the transition regular expression between those two states will characterize the regular expression of the original DFA. 

### DFA - optimized DFA

The Myhill Nerode theorem can be used to optimize DFAs. The algorithm marks all state pairs that transition to a pair of accept and non-accept states on receiving the same input alphabet initially. The marked state pairs will not be merged as accept and non-accept states can't be merged into a single state. After this operation we consider all the transitions for a single alphabet from every state pair, and if it leads to a marked pair we mark the state pair. If on receiving the same alphabet a state pair transitions to a marked pair, then the pair can't be merged as they lead to distinct elements on a second transition and hence aren't equivalent. After finishing the marking process, the states that are unmarked and share common states are merged, and the states that do not exist in the final state list are entered as is. For example if our original set of states is `a, b, c, d, e, f` and the unmarked state pairs after the operation are `{a, b}, {c, d}, {d, e}, {c, e}` , our final set of states will be `{a, b}, {c, d, e}, f` . The transitions from these states will be the same as the transitions from any one of the states that belong to the set, and instead of leading to a single state the transition will terminate in a set of states.