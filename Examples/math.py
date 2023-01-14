import sys
sys.path.insert(0,'..')

from scanner_automaton import *

if __name__ == "__main__":
    automaton = ScannerAutomaton(ignores=" \t")
    automaton.define_numbers("Operand")
    automaton.define_letters("Variable")
    automaton.define_state("\n", "NewLine")
    automaton.define_state("+", "Plus", "")
    automaton.define_state("-", "Minus", "")
    automaton.define_state("*", "Factor", "")
    automaton.define_state("/", "Divide", "")
    automaton.define_state("%", "Modulo", "")
    automaton.define_state("(", "Left Par", "")
    automaton.define_state(")", "Right Par", "")
    automaton.define_state("=", "Equal", "")
    automaton.input("a = 2 + 1\nb = a - 10\nc = a * b\nd = (b / c) % a")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()