import sys
import json
from graphviz import Digraph

ALLOWED = "0123456789qwertyuiopasdfghjklzxcvbnm*.+()$"
OPS = "*.+()"
PRIORITY = {'*': 2, '.': 1, '+': 0}
INVALID_RE = -1
VALID_RE = 0

class State:
    id = 0

    def __init__(self): # constructor, se llama cuando se crea una nueva instancia de "State".
        self.id = State.id  
        self.name = "" # luego se usa para dar nombre a los estados: "q1", "q2", etc.
        State.id += 1
        self.transitions = [] # servirá para almacenar las transiciones desde este estado hacia otros.

    def addTransition(self, node, alph): # agrega una transición desde el estado actual (self) a otro (node) usando un símbolo del alfabeto (alph).
        self.transitions.append((node, alph)) # agrega una tupla a la lista de transiciones.

class NFA:
    def __init__(self):
        self.states = [] # lista para almacenar todos los estados.
        self.start = None # estado inicial, inicialmente se establece como "None".
        self.accept = [] # Lista que contiene los estados de aceptación del NFA.
        self.alphabet = [] # Lista que contendrá el alfabeto del NFA.

    # toma una expresión regular RE como argumento y analiza sus caracteres para construir el alfabeto del NFA.

    def getAlph(self, RE): 
        for c in RE:
            if c not in OPS and c not in self.alphabet:
                self.alphabet.append(c)

    def getStart(self): # retorna el estado incial.
        return self.start 

    def getAccept(self): # retorna el estado de aceptación.
        return self.accept

    def addState(self, s): # recibe un objeto s de tipo State y lo añade a la lista de estados del NFA
        self.states.append(s)

    # facilita la adición de una transición entre dos estados s1 y s2 con un símbolo de transición a. 
    # Este método llama al método addTransition del estado s1, que pertenece a la clase State, para agregar la transición.    
    def addTransition(self, s1, s2, a):
        s1.addTransition(s2, a)

    # establece el estado inicial del NFA (self.start) al estado s pasado como argumento.
    def makeStart(self, s):
        self.start = s

    # agrega el estado s a la lista de estados de aceptación del NFA.
    def makeAccept(self, s):
        self.accept.append(s)

    # elimina el estado s de la lista de estados de aceptación del NFA.
    def removeAccept(self, s):
        self.accept.remove(s)

    # asigna nombres unicos a todos los estados.
    def names(self):  
        c = 0
        self.start.name = f"q{c}" # se le asigna de nombre q0.

        # utiliza un enfoque de búsqueda en anchura (BFS) para recorrer todas las transiciones de los estados. 
        # Por cada estado no nombrado encontrado, se le asigna un nombre único incrementando el contador c 
        # y se agrega a la lista states para su posterior procesamiento.

        c += 1
        states = [self.start] 
        while states:
            cur = states.pop(0)
            for state, alph in cur.transitions:
                if not state.name:
                    state.name = f"q{c}"
                    c += 1
                    states.append(state)

    # genera y guarda la representación del NFA como JSON.
    def printTuple(self, path):
        js = {
            'states': [state.name for state in self.states], # Lista de nombres de todos los estados
            'letters': self.alphabet, # Alfabeto
            'transition_function': [ # Lista de listas de transiciones.
                [state.name, alph, node.name]
                for state in self.states
                for node, alph in state.transitions
            ],
            'start_states': [self.start.name], # Lista con el nombre del estado inicial.
            'final_states': [state.name for state in self.accept] # Lista de nombres de los estados de aceptación.
        }
        with open(path, 'w') as f:
            json.dump(js, f, indent=4)

# toma una expresión regular RE como argumento 
# y devuelve una versión modificada de RE con operadores de concatenación . añadidos donde sea necesario.            
def addConcat(RE):
    res = [] # aquí vamos a almacenar la expresión modificada
    for i in range(len(RE)): # itera sobre cada índice i en el rango de la longitud de la cadena.
        res.append(RE[i]) # copia directamente cada carácter de RE a res.
        if RE[i] not in '(.+': #  Verifica si el carácter actual RE[i] no es (/./+ 
            if i + 1 < len(RE) and RE[i + 1] not in ')*+.': # verifica si no le sigue )/*/.
                res.append('.') # se agrega un operador de concatenación
    return "".join(res) # Une todos los elementos de la lista res en una cadena única 

def parseRE(RE, postfix):
    # No eliminar espacios en blanco de la expresión regular aquí
    # RE = RE.replace(" ", "")

    if RE == "" or RE == " ":
        return VALID_RE

    #  Itera sobre cada carácter a para ver si es o no permitido.
    for a in RE:
        if a not in ALLOWED:
            return INVALID_RE

    postfix.clear() # limpiamos la lista.
    stack = [] # inicializamos una pila vacía.
    for a in RE:
        if a not in OPS:
            postfix.append(a)
        elif a == '(':
            stack.append('(') # se coloca en la pila.
        # Se sacan los operadores de la pila y se colocan en postfix hasta encontrar la pareja del parentesis.
        # Luego se elimina el parentesis izquierdo de Slack.
        elif a == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        # Maneja los operadores según su prioridad. 
        else:
            while stack and stack[-1] != '(' and PRIORITY[a] <= PRIORITY[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(a)
    while stack: # se sacan todos los operadores restantes de la pila stack y se añaden a postfix.
        postfix.append(stack.pop())
    return VALID_RE # la expresion es valida.

def readJSON(path):
    with open(path, "r") as f:
        data = json.load(f) # Lee el contenido del archivo JSON y lo carga en la variable.
    return data.get('RE', '') # Accede al diccionario data y obtiene el valor asociado con la clave 'RE'. 
                                 # Si la clave 'RE' no existe en el diccionario data, devuelve una cadena vacía ''.

def visualize_nfa(nfa_json, output_path): # recibe el archivo json y la ruta para guardar el grafico.
    dot = Digraph() # creamos un objeto dot vacío.
    dot.attr(rankdir='LR')  # establece la posicion en horizontal.
    # Recorremos todos los estados en la lista.
    for state in nfa_json["states"]: 
        if state in nfa_json["final_states"]:
            dot.node(state, shape='doublecircle') # crea un nodo con forma de doble círculo --> estado final
        else:
            dot.node(state) # crea un normal.
    for transition in nfa_json["transition_function"]:
        start_state, symbol, end_state = transition
        if symbol == "$":
            label = "ε" 
        else:
            label = symbol # se usa el propio simbolo como etiqueta.
        dot.edge(start_state, end_state, label=label) # arista dirigida desde start_state hasta end_state con la etiqueta label.
    for start_state in nfa_json["start_states"]:
        dot.node("start", shape="point")
        dot.edge("start", start_state) # arista dirigida desde start a start_state.
    dot.render(output_path, format='png', cleanup=True) # se genera como png.


def kleene_base_cases(symbol):
    if symbol == '$':
        nfa = NFA() # nueva instancia asignado a la variable nfa.
        start_state = State() # crea un nuevo estado inicial.
        nfa.addState(start_state) # añadimos el estado. 
        nfa.makeStart(start_state) # se marca como estado inicial.
        nfa.makeAccept(start_state) # se marca como estado de aceptacion.
        return nfa 
    if symbol == '' or symbol == ' ' or symbol == None:
        nfa = NFA() # nueva instancia asignado a la variable nfa.
        start_state = State() # crea un nuevo estado inicial.
        nfa.addState(start_state) # añadimos el estado.
        nfa.makeStart(start_state)  # se marca como estado inicial.
        return nfa
    else:
        nfa = NFA()  # nueva instancia asignado a la variable nfa.
        q0 = State()
        nfa.addState(q0) 
        nfa.makeStart(q0) # se añade como estado inicial.
        q1 = State()
        nfa.addState(q1)
        nfa.makeAccept(q1) # se añade como estado de aceptacion.
        nfa.addTransition(q0, q1, symbol) # se añade la transicion con el simbolo especificado.
        return nfa

def kleene_union(nfa1, nfa2): # une dos automatas.
    nfa = NFA()
    start = State()
    nfa.addState(start)
    nfa.makeStart(start)
    # Añade transiciones desde el estado inicial start del NFA nfa hacia los estados iniciales 
    # de nfa1 y nfa2 utilizando '$' como símbolo de transición. 
    nfa.addTransition(start, nfa1.start, '$')
    nfa.addTransition(start, nfa2.start, '$')
    nfa.states += nfa1.states + nfa2.states # Concatena las listas de estados (states) de nfa1 y nfa2.
    nfa.accept = nfa1.accept + nfa2.accept # Concatena las listas de estados de aceptación (accept) de nfa1 y nfa2.
    return nfa

def kleene_concat(nfa1, nfa2): # concatena dos automatas
    nfa = NFA()
    nfa.states = nfa1.states + nfa2.states # Concatena las listas de estados (states) de nfa1 y nfa2 
    nfa.start = nfa1.start # Nos aseguramos que la concatenacion empiece desde el estado inicial de nfa1.
    nfa.accept = nfa2.accept # La cadena debe llegar a uno de los estados de aceptacion de nfa2 para que sea exitosa.
    for accept_state in nfa1.accept:
        accept_state.addTransition(nfa2.start, '$') # representa la conexión entre el último estado de nfa1 y el primer estado de nfa2 en la concatenación.
        nfa1.removeAccept(accept_state) # Elimina el estado de aceptación de nfa1.
    return nfa

def kleene_star(nfa1):
    nfa = NFA()
    start = State()
    nfa.addState(start)
    nfa.makeStart(start) #  Marca el estado start como el estado inicial.
    nfa.addTransition(start, nfa1.start, '$') # Añade una transición  epsilon desde el estado inicial start del NFA hacia el estado inicial de nfa1.
    for accept_state in nfa1.accept:
        nfa.addTransition(accept_state, nfa1.start, '$') # añade una transicion epsilon desde el estado de aceptacion hasta el inicial de nfa1.
        nfa.addTransition(accept_state, start, '$') # añade una transicion epsilon desde el estado de aceptacion hacia start.
    nfa.states += nfa1.states # Concatena las listas de estados (states) de nfa1 y las añade a nfa.states.
    nfa.accept.append(start) # añade start a la lista de estados de aceptacion de nfa.
    return nfa

def thompson(RE):
    postfix = [] # se utilizará para almacenar la versión postfix (postfija) de la expresión regular.
    #  Llama a la función addConcat() para agregar un símbolo de concatenación implícito en la expresión regular 
    # y luego llama a parseRE() para convertir la expresión regular en formato postfix y almacenarla en postfix
    if parseRE(addConcat(RE), postfix) == INVALID_RE:
        raise ValueError("Invalid regular expression")

    # Verifica si postfix está vacío. Si es así, significa que la expresión regular era una cadena vacía o espacio en blanco, 
    # devuelve un NFA básico que acepta la cadena vacía.
    if not postfix:
        nfa = NFA()
        start_state = State()
        nfa.addState(start_state)
        nfa.makeStart(start_state)
        return nfa

    stackNFA = []
    for symbol in postfix:
        if symbol not in OPS:
            stackNFA.append(kleene_base_cases(symbol)) # crea un NFA básico y lo apila en stackNFA.

        # Si es + desapila dos NFAs (N2 y N1), aplica la unión (kleene_union(N1, N2)) y apila el resultado en stackNFA.
        elif symbol == '+':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            stackNFA.append(kleene_union(N1, N2))
        
        # desapila dos NFAs (N2 y N1), aplica la concatenación (kleene_concat(N1, N2)) y apila el resultado en stackNFA.
        elif symbol == '.':
            N2 = stackNFA.pop()
            N1 = stackNFA.pop()
            stackNFA.append(kleene_concat(N1, N2))

        # desapila un NFA (N), aplica la operación estrella (kleene_star(N)) y apila el resultado en stackNFA.
        elif symbol == '*':
            N = stackNFA.pop()
            stackNFA.append(kleene_star(N))

    if not stackNFA:
        raise ValueError("Invalid regular expression")

    return stackNFA[0]

def main():

    # Debemos recibir 3 argumentos, sino explica cómo.
    if len(sys.argv) != 3:
        print("Usage: python RE-NFA.py <input_json> <output_json>")
        exit()

    RE = readJSON(sys.argv[1])
    if not RE: #  Verifica si RE está vacía después de leer desde el archivo. Si es así, asigna una cadena vacía "" a RE.
        RE = ""

    nfa = thompson(RE) # convertimos la expresión regular RE en un autómata finito no determinista (NFA) y asignamos el resultado a nfa.
    nfa.getAlph(RE) # obtenemos el alfabeto.
    nfa.names() # asignamos los nombres unicos.
    output_path = sys.argv[2] # asignamos la ruta del output.
    nfa.printTuple(output_path) # genera y guarda la representación del autómata nfa como un archivo JSON en la ruta.

    # abrimos el archivo y llamamos a la funcion para visualizar el automata.
    with open(output_path, 'r') as f:
        nfa_json = json.load(f)
    visualize_nfa(nfa_json, output_path.replace('.json', ''))

if __name__ == "__main__":
    main()
