import string

# Utility class containing the internal states during runtime of a scanner
class ScannerAutomatonInternals:
    def __init__(self, buffer):
        self.col = 0
        self.line = 1
        self.buffer = buffer
        self.idx = -1
        self.cur = None

class ScannerAutomatonState:
    def __init__(self, trigger, reflective_condition, token):
        self.trigger = trigger        
        self.reflection = reflective_condition
        self.token = token

    def transition_active(self, target):
        return target in self.trigger

    def reflection_active(self, target):
        return target in self.reflection


class ScannerAutomatonToken:
    def __init__(self, col, line, token, value):
        self.col = col
        self.line = line
        self.token = token
        self.value = value

    def __str__(self) -> str:
        return f"{self.token} at {self.line}, {self.col} with value {self.value}"

# Automaton-based generic scanner
class ScannerAutomaton:
    SCANNER_EOF = "<EOF>"

    def __init__(self, ignores = ""):
        self.states = []
        self.ignores = ignores
        self.internals = None

    def define_state(self, trigger:str, token, reflection:str = None):
        if reflection is None:
            reflection = trigger
        state = ScannerAutomatonState(trigger, reflection, token)
        self.states.append(state)

    def define_numbers(self, token):
        state = ScannerAutomatonState(string.digits, string.digits, token)
        self.states.append(state)

    def define_letters(self, token):
        state = ScannerAutomatonState(string.ascii_letters, string.ascii_letters, token)
        self.states.append(state)

    def input(self, buffer):
        self.internals = ScannerAutomatonInternals(buffer)
        self.move_cursor()

    def move_cursor(self):
        if self.internals is not None and self.internals.cur != ScannerAutomaton.SCANNER_EOF:
            self.internals.idx += 1
            if self.internals.idx < len(self.internals.buffer):
                self.internals.cur = self.internals.buffer[self.internals.idx]
                self.internals.col += 1
                if self.internals.cur == '\n':
                    self.internals.col = 0
                    self.internals.line += 1
            else:
                self.internals.cur = ScannerAutomaton.SCANNER_EOF           

    def next_token(self)->ScannerAutomatonToken:
        while self.internals.cur in self.ignores:
            self.move_cursor()

        if self.internals.cur == ScannerAutomaton.SCANNER_EOF:
            return ScannerAutomatonToken(self.internals.col, self.internals.line, None, None)
        active_states = [state for state in self.states if state.transition_active(self.internals.cur)]            
        if len(active_states) == 0:
            raise ValueError(f"Unexpected token in line {self.internals.line} column {self.internals.col}: {self.internals.cur}")
        
        last_states = active_states
        value = self.internals.cur
        self.move_cursor()
        while any([state.reflection_active(self.internals.cur) for state in active_states]):
            value += self.internals.cur
            self.move_cursor()
            last_states = active_states
            active_states = [state for state in active_states if state.reflection_active(self.internals.cur)]

        if len(last_states) > 1:
            raise ValueError(f"Non-Determinism detected! Input {value} ends in states {','.join([x.token for x in last_states])}")

        return ScannerAutomatonToken(self.internals.col, self.internals.line, last_states[0].token, value)

    
if __name__ == "__main__":
    #Minimal Example: 
    automaton = ScannerAutomaton(ignores=",")
    automaton.define_numbers("Number")
    automaton.define_letters("Word")
    automaton.input("11,abc,66,a5,8z")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()

    #Minimal QDIMACS:
    automaton = ScannerAutomaton(ignores=" \t")
    automaton.define_letters("Quantifier")
    automaton.define_numbers("Variables")
    automaton.define_state("\n", "NewLine")
    automaton.define_state("-", "Minus")
    automaton.input("p cnf 3 3\na 1 0\nb 2 0\n1 2 0\n-1 2\n")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()

    #Non Determinism:
    automaton = ScannerAutomaton(ignores=" ")
    automaton.define_state("a", "abc", "abc")
    automaton.define_state("a", "abx", "abx")
    automaton.input("abc abcc abbbc abxb accbc aaxbb")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()

