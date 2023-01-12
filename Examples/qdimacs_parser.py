import sys
sys.path.insert(0,'..')

from scanner_automaton import *

if __name__ == "__main__":
    automaton = ScannerAutomaton(ignores=" \t")
    automaton.define_state("p","preamble p", "")
    automaton.define_keyword("cnf","preamble cnf")
    automaton.define_state("e","Exists", "")
    automaton.define_state("a", "Forall", "")
    automaton.define_numbers("Variable")
    automaton.define_state("\n", "NewLine")
    automaton.define_state("-", "Minus")
    automaton.input("p cnf 3 3\na 1 0\ne 2 0\n1 2 0\n-1 2\n")
    token = automaton.next_token()
    while token.token is not None:
        print(token)
        token = automaton.next_token()