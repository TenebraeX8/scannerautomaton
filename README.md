# Scanner-Automaton

When custom-writing a parser, writing its scanner feels like copying the whole code from a previous project with only very minor changes. 
In order to avoid copying, I thought of an approach of generalizing a scanner by constructing a semi-non-deterministic state-machine.


## Theory
We are interested in converting raw characters into a stream of token relevant for the parser. 
* Each possible token is described by a state in the automaton.
* A state consists of two parts
  * An activation condition (trigger) allowing the state to be entered 
  * A reflective condition which describes a reflective edge. This is the condition whether the scanner stays in this state when already entered
* The scanner can be in multiple states at once (non-determinism)
  * As long as any state is still active, the scanner continues on this token
  * If no state is active anymore, the last state wins and its associated token is returned
  * This has to be unambiguous at this point (restriction on non-determinism)

## Keywords
It is very common for the reflective condition to change with each input (allowing only a specific stream) as well as not allowing every intermediate state, i.e. having keywords.
* A Keyword is a more special state
  * Trigger is the first character of the associated keyword
  * Instead of a subset of the alphabet, we have a reflective-function which determines the truth value of the current input and thus decides over transitions
  * The reflective condition enforces the following invariant:
    * The current input is equal to the keyword of the state up to its length
    * The current input's length is smaller or equal to the keyword's length
  * A Keyword will always win over a general state
    * i.e. if you have a alphabetic keyword and also a state allowing all words, even though this would be unambiguous the keyword will win in this case.
    
    
## Examples
In the folder "examples" there are some example usages of the scanner automaton to make it easier for you to use it.

## Implementing it
Use standard "import scanner_automaton" while having the python script in your main-directory.

Some (useful) tips:
* In most of the cases you do not have to understand in detail how the states work ;) Just have a look at the methods provided and you will get an idea
* Define your rules as strong as possible in order to avoid unambiguous behaviour in the states.
  * But you don't have to worry about e.g. keywords in this context as they are treated specially
  
  
