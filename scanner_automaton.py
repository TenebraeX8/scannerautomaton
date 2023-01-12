import string

# Utility class containing the internal states during runtime of a scanner
class ScannerAutomatonInternals:
    def __init__(self, buffer):
        self.col = 0
        self.line = 1
        self.buffer = buffer
        self.idx = -1
        self.cur = None

# Represents the state of a Scanner Automaton
# param trigger: string containing the chars which trigger the transition to this state to be active
# param reflective_condition: string containing the chars which allows transitioning to the same state
# param token: the token associated with the state
class ScannerAutomatonState:
    def __init__(self, trigger, reflective_condition, token):
        self.trigger = trigger        
        self.reflection = reflective_condition
        self.token = token

    #Indicates, whether the transition to this state is active with the current target
    def transition_active(self, target):
        return target in self.trigger

    #Indicates, whether it is possible to stay in this state with the current target
    def reflection_active(self, target):
        return target in self.reflection

    #Is called when a reflective transition happens (empty by default, can be overwritten in subclass)
    def reflective_transition(self, value):
        pass

    #Is called when a transition happens (empty by default, can be overwritten in subclass)
    def transition(self):
        pass

    def finial_state(self):
        return True

#Only allows a special sequence 
class ScannerAutomationKeywordState(ScannerAutomatonState):
    def __init__(self, keyword, token):
        if len(keyword) < 1: 
            raise ValueError("Empty Keyword is illegal!")
        reflection = "" if len(keyword) < 2 else keyword[1]
        super().__init__(keyword[0], reflection, token)
        self.keyword = keyword
        self.buffer = keyword[0]

    #Indicates, whether the transition to this state is active with the current target
    def transition_active(self, target):
        return target in self.trigger

    #Indicates, whether it is possible to stay in this state with the current target
    def reflection_active(self, target):
        return self.keyword.startswith(self.buffer+target) and len(self.buffer+target) <= len(self.keyword)

    def reflective_transition(self, value):
        self.buffer = value
        
    def transition(self):
        self.buffer = self.keyword[0]

# A dataclass for the returned token of the Scanner
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

    #Constructor
    #param ignores: a string containing the chars skipped by the scanner
    def __init__(self, ignores = ""):
        self.states = []
        self.ignores = ignores
        self.internals = None

    #defines a state for the scanner
    #param trigger: string containing the chars which allow to enter this state
    #param token: the token associated with this state
    #param reflection: string containing the chars allowing to stay in the state once entered. If None, it is equal to the trigger
    def define_state(self, trigger:str, token, reflection:str = None):
        if reflection is None:
            reflection = trigger
        state = ScannerAutomatonState(trigger, reflection, token)
        self.states.append(state)

    def define_keyword(self, keyword:str, token):
        state = ScannerAutomationKeywordState(keyword, token)
        self.states.append(state)

    #defines a token for scanning a simple sequence of number
    def define_numbers(self, token):
        state = ScannerAutomatonState(string.digits, string.digits, token)
        self.states.append(state)

    #defines a token for scanning a simple sequence of letters
    def define_letters(self, token):
        state = ScannerAutomatonState(string.ascii_letters, string.ascii_letters, token)
        self.states.append(state)

    #initializes the scanner on a specific input
    #param buffer: the string to be scanned
    def input(self, buffer):
        self.internals = ScannerAutomatonInternals(buffer)
        self.move_cursor()

    #Get the next char from the buffer
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

    #Scan a single state and get the next token
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
            [state.reflective_transition(value) for state in active_states]
            [state.transition() for state in active_states if not state.reflection_active(self.internals.cur)]
            active_states = [state for state in active_states if state.reflection_active(self.internals.cur)]

        #print(value)
        #print([state.keyword for state in last_states if isinstance(state, ScannerAutomationKeywordState)])
        last_states = [state for state in last_states if not isinstance(state, ScannerAutomationKeywordState) or value == state.keyword]

        if len(last_states) > 1:
            #If it matches exactly one keyword, this has higher precedence
            keywords = [x for x in last_states if isinstance(x, ScannerAutomationKeywordState)]
            if len(keywords) == 1: 
                last_states = keywords
            else:
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
    print()
    #Keyword
    automaton = ScannerAutomaton(ignores=" ")
    automaton.define_letters("Letter")
    automaton.define_keyword("Key", "Keyword")
    automaton.input("abc Key Keeey Ke Keyy KKey")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()    

