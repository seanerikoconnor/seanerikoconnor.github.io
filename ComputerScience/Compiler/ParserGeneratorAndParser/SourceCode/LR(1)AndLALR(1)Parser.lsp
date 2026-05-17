#|-----------------------------------------------------------------------------

NAME

   LR(1)AndLALR(1)Parser.lsp

DESCRIPTION

    Bottom up LR(1)/LALR(1) parser.  It halts and either accepts a sentence in
    an LR(1) or LALR(1) grammar or it prints an error message.  


CALLING SEQUENCE

    Once you are in a Common Lisp interpreter, load this file,

       (load "LR(1)AndLALR(1)Parser.lsp")

    The normal calling sequence is 

       (parser "parse-tables.dat" "parse-input.dat" "parse-output.dat")

    You can do an automated test it by calling,

        (test-parser)

    you may have to change the base directory location in the function test-parser.

    Online documentation when you're in the lisp interpreter is given by the
    standard documentation function,

        (apropos 'element-of?)
            => ELEMENT-OF?
        (documentation 'element-of? 'function)
        (documentation '*productions* 'variable)


INPUT FILES:

        parse-tables.dat   A numbered list of productions for the grammar,
                           followed by the LR(1) or LALR(1) parsing action and 
                           goto tables, followed by a table of error messages.
                           See the file parse-tables.dat for an example.

        parse-input.dat    A sequence of sentences to parse.  See the file
                           parse-input.dat for an example.

        You can use UNIX's yacc compiler-compiler to generate the parse tables 
        above.  Run yacc with the -v option.  It generates the y.output file 
        which contains the parsing action and goto tables.

        You can also run my program LR(1)AndLALR(1)ParserGenerator.lsp   
        to get the action and goto tables.

        You'll need to create the error messages yourself, either by looking at
        the goto graph output of LR(1)AndLALR(1)ParserGenerator.lsp   
        or by the state of the parse in yacc's y.output file.


OUTPUT FILES:

        parse-output.dat  The results of the parse on the input file.  See
                         "parse-output.dat" for an example of correct output.


METHOD

        We use algorithm 4.7 [Aho 86, pgs. 216-220] which works like this:

        The initial parser configuration is

            (s0 | a1 ... an $)

        where a1 ... an is the input and s0 = 0 is the initial state.
        The parse stack is to the left of the bar and the unprocessed
        input is to the right.  Now suppose the configuration is

            (s0 x1 ... xm sm | ai ai+1 ... an $)

        There are four possible things we can do:

        (1)  Shift the input.  ACTION[ sm, ai ] = shift s    

             (s0 X1 ... Xm sm ai s | ai+1 ... an $)

        (2)  Reduce.  ACTION[ sm, ai ] = reduce( A -> beta )

             (s0 X1 ... Xm-r sm-r A s | ai ai+1 ... an $)

             where s = GOTO[ sm-r, A ] and r = length( beta )

        (3)  Accept (i.e. halt).  ACTION[ sm, ai ] = accept

             The sentence is in the grammar;  we halt and accept it.

        (4)  Abort with error.  ACTION[ sm, ai ] = error

             We produce the error message using the current parsing state 
             lookahead symbol ai.

REFERENCES

        See http://www.seanerikoconnor.freeservers.com for a review of the
        parsing theory behind this program.


        [Aho 86]  COMPILERS: PRINCIPLES, TECHNIQUES, AND TOOLS,
                  Alfred V. Aho, Ravi Sethi, and Jeffrey D. Ullman,
                  Addison-Wesley, 1986.

        [Aho 74]  "LR Parsing", Alfred V. Aho and Stephen C. Johnson, 
                  Computing Surveys, Vol. 6, No. 2, June 1974, pg. 99-124.


AUTHOR

     Sean E. O'Connor        06 Jun 1989  Version 1.0

LEGAL

    LR(1)AndLALR(1)ParserGenerator Version 5.6 
    An LR(1) and LALR(1) Parser Generator written in Common Lisp.

    Copyright (C) 1989-2026 by Sean Erik O'Connor.  All Rights Reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    The author's address is seanerikoconnor!AT!gmail!DOT!com
    with the !DOT! replaced by . and the !AT! replaced by @

BUGS

    We'd like to modify the data type of the stack elements so we can
    associate a semantic action with each reduction.

-----------------------------------------------------------------------------|#


; ------------------------------------------------------------------------------
; |                            Global Variables                                |
; ------------------------------------------------------------------------------

(defvar *productions*  nil 
" List of productions of the unaugmented grammar."
)

(defvar *action-table* nil)   ; LR(1) or LALR(1) action table.

(defvar *goto-table*   nil)   ; LR(1) or LALR(1) goto table.

(defvar *error-message* nil)   ; Table of error message for each state.

(defvar *input-stack* nil)   ; Input stack of not yet processed symbols.

(defvar *old-input-stack* nil)   ; Already processed input.

(defvar *parse-stack* nil)   ; Parser stack.

(defvar *terminals* nil)

(defvar *goto-graph* nil)

    (proclaim '(special *goto-table*))
    (proclaim '(special *error-messages*))

    (proclaim '(special *input-stack*))
    (proclaim '(special *old-input-stack*))
    (proclaim '(special *parse-stack*))

;  DATA STRUCTURES

;  *productions*   = (PRODUCTION1 PRODUCTION2...)
;  production      = (A -> B C D ...)


;  *action-table*  = (TABLE-LINE1 TABLE-LINE2 ...)
;  table-line      = ((STATE1 STATE2 ...) LIST-OF-ACTIONS)
;  list-of-actions = (ACTION-PAIR1 ACTION-PAIR2 ...)
;  action-pair     = (TRIGGER-SYMBOL ACTION)
;  action          = (S i), (R i), (ACC NIL) 

;  *goto-table*    = (TABLE-LINE1 TABLE-LINE2 ...)
;  table-line      = ((STATE1 STATE2 ...) LIST-OF-GOTOS)
;  list-of-gotos   = (GOTO-PAIR1 GOTO-PAIR2 ...)
;  goto-pair       = (TRIGGER-SYMBOL GOTO-STATE)
;  trigger-symbol  = any nonterminal or DEFAULT
;
; ------------------------------------------------------------------------------



; ------------------------------------------------------------------------------
; |                          print-legal-notice                                |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Write legal notice when the program starts up.
;
;  CALLING SEQUENCE
;
;      Returns:      Legal notice to standard output.
;
;  EXAMPLE
;
; ------------------------------------------------------------------------------

(defun print-legal-notice()

    ; Print a few newlines, the notice and a few more newlines.
    (format t "~%~%~A~%~%" 
        "
    LR(1)AndLALR(1)Parser Version 5.6
                
    An LR(1) and LALR(1) Parser written in Common Lisp.
                
    Copyright (C) 1989-2026 by Sean Erik O'Connor.  All Rights Reserved.
                
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    The author's address is seanerikoconnor!AT!gmail!DOT!com
    with the !DOT! replaced by . and the !AT! replaced by @"
                
    )
)



; ********************************* Input I/O ********************************


; ------------------------------------------------------------------------------
; |                              print-file-to-console                         |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      List the lines of a file to the console.
;
;  CALLING SEQUENCE
;
;      (print-file-to-console filename)
;
;      filename  Name of the file.
;
;      Returns:  
;
;  EXAMPLE
;
;      (print-file-to-console "grammar.dat") 
;      =>      ;  GrammarE=E+T_T.dat
;              ---------------------------------------------------------------------------
;
;              A grammar of arithmetic expressions,
;
;              E -> E + T | T
;              ...
;
; ------------------------------------------------------------------------------

(defun print-file-to-console( file-name )
    (format t "~%~%=========================== ~A =============================~%~%~%" file-name)

    (with-open-file (stream file-name)
      (do ( (line (read-line stream nil)    ; nil inhibits throw at eof
                  (read-line stream nil) )  ; and read-line returns nil at eof
          )
          ( (null line) )  ; Terminate at eof
          (format t "~A~%" line)
      )
    )
)

; ------------------------------------------------------------------------------
; |                         load-input-initialize-parser                       |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Load the productions and the parsing action and goto tables from file.
;
;  CALLING SEQUENCE
;
;      (load-input-initialize-parser filename)
;
;      filename  Name of the file containing a numbered list of productions,
;                the parsing action and goto tables, and error messages.
;
;      Returns:  
;                *productions*, *action-table*, *goto-table*, *error-messages*, 
;                set to their values in the file.  *parse-stack*, *input-stack*,
;                and *old-input-stack* are set to nil.
;
;  EXAMPLE
;
;      (load-input-initialize-parser "parse-tables.dat") 
;      *productions* => ( ((1) (E -> E + T)) 
;                         ((2) (E -> T))
;                         ((3) (T -> T * F)) 
;                         ((4) (T -> F))
;                         ((5) (F -> [ E ])) 
;                         ((6) (F -> ID))    )
;
; ------------------------------------------------------------------------------

(defun load-input-initialize-parser( parsing-tables-file )


(let ( (fp (open parsing-tables-file :direction :input)) )

    (setq *terminals*      (read fp))
    (setq *productions*    (read fp))
    (setq *goto-graph*     (read fp))
    (setq *action-table*   (read fp))
    (setq *goto-table*     (read fp))
    (setq *error-messages* (read fp))

    (setq *parse-stack* nil)
    (setq *input-stack* nil)
    (setq *old-input-stack* nil)

    (close fp))
)




; ************************** General List Manipulation *************************

(defun element-of?( element list &key (test NIL) )
"
   DESCRIPTION
 
       Find out if an atom or a list is a member of a given list.
 
   CALLING SEQUENCE
  
       (element-of? element list :test test)
           => T if element is in list; NIL if not.
 
       test        The name of the function which tests if two symbols are 
                   equal.  It should be a function of two arguments which
                   returns T if the symbols are equal and NIL otherwise.
                   test defaults to NIL, in which case we use #'equal to 
                   compare.
 
   EXAMPLE
 
       (element-of? '(hot dog) '((cool cat) (cool dog))) => NIL
 
       (defun no-value-judgements( s1 s2 ) (equal (second s1) (second s2)))
 
       (element-of? '(hot dog) '((cool cat) (cool dog))
                    :test 'no-value-judgements) => T
"

(cond ( (null list) nil)                        ; Not in the list.

      ( (if (not (null test))                   ; First item matches...
        
            (funcall test element (first list)) ; ... according to test function

            (equal element (first list)))       ; ... according to equal.

                         t)

      ( t  (element-of? element (rest list)     ; Try again on rest of list.
                        :test test))) 
)




; ------------------------------------------------------------------------------
; |                           rfirst, rrest and rcons                          |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Reversed versions of first (car), rest (cdr) and cons.
;
;  CALLING SEQUENCE
; 
;      (rfirst list) => Last element in list.  
;      (rfirst nil) => nil
;      (rrest list) => List with last element deleted. 
;      (rfirst nil) => nil
;      (rcons atom list) => List with atom appended to the end.
;
;  EXAMPLE
;
;      (rfirst '(I am fnugled)) => fnugled
;      (rrest  '(I am fnugled)) => (I am)
;      (rcons  'fnugled '(I am)) => (I am fnugled)
;
; ------------------------------------------------------------------------------

(defun rfirst( list ) 
    
    (first (reverse list))
)

(defun rrest( list ) 
    
    (reverse (rest (reverse list)))
)

(defun rcons( atom list ) 
    
    `(,@list ,atom)
)




; ********************************* Predicates *********************************

; ------------------------------------------------------------------------------
; |                       shift?, reduce?, accept? and error?                  |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Operators to recognize different parsing actions.
;
;  CALLING SEQUENCE
; 
;      (shift?  action)
;      (reduce? action)
;      (accept? action)
;      (error?  action)
;
;      action       The code for the action to perform from the parsing
;                   action table.
;
;      Returns:     T if the action matches the code.
;
;  EXAMPLE
;
;      (shift?  '(s 5)) => T
;      (reduce? '(r 3)) => T
;      (accept? '(acc nil)) => T
;      (error?  '(error "sample error message")) => T
;
; ------------------------------------------------------------------------------

(defun shift?( action )

    (equal (first action) 's)
)

(defun reduce?( action )

    (equal (first action) 'r)
)

(defun accept?( action )

    (equal (first action) 'acc)
)

(defun error?( action )

    (equal (first action) 'error)
)




; ********************************* Table Lookup *******************************

; ------------------------------------------------------------------------------
; |                                  list-lookup                               |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Lookup an item in a line of an action, goto or error message table by
;      state and by symbol.
;
;  CALLING SEQUENCE
; 
;      (list-lookup symbol table :table-type type)
;
;      symbol      The transition symbol for action or goto.  Ignored when
;                  looking up an error message.  You can set it to nil.
;
;      list        A line of an action, goto or error message table to search.
;
;      table-type  The type of table to lookup in:  'action or 'goto.
;                  Defaults to 'action.
;
;      Returns:    The action to take (for an action table) or the new state
;                  (for a goto table).
;
;  EXAMPLE
;
;      Please refer to the file parse-tables.dat.
;
;      (list-lookup 'ID '( ([ (S 4)) (ID (S 5)) (DEFAULT ERROR) )
;                   :table-type 'action) => (S 5)
;
;      (list-lookup 'F '( (T 9) (F 3) (DEFAULT ERROR) ) :table-type 'goto) => 3
;
; ------------------------------------------------------------------------------

(defun list-lookup( symbol list &key (table-type 'action) )

(cond ( (or (equal (first (first list)) symbol)    ; Found symbol.
            (equal (length list) 1))               ; Not found - use default
                                                   ; (last) item.
           (cond ( (or (equal table-type 'action)
                       (equal table-type 'goto))

                     (second (first list)))))


      ( t  (list-lookup symbol (rest list) :table-type table-type)))
)


; ------------------------------------------------------------------------------
; |                                 table-lookup                               |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Lookup an item in an action, goto or error message table by state and 
;      by symbol.
;
;  CALLING SEQUENCE
; 
;      (table-lookup state symbol table :table-type type)
;
;      state       The number of the state or production.
;
;      symbol      The transition symbol for action or goto.  Ignored when
;                  looking up an error message or production.  Set it to
;                  nil for these two cases.
;
;      table       The action, goto or error message table to search in.
;
;      table-type  The type of table to lookup in:  'action, 'goto, 
;                  'error-message or 'production.  Defaults to 'action.
;
;      Returns:    The action to take (for an action table), the new state
;                  (for a goto table), the error message (for an error message
;                  table) the production (for the list of productions).  
;                  We return NIL if state was not found.
;
;  EXAMPLE
;
;      Please refer to the file parse-tables.dat.
;
;      (table-lookup 6 'ID *action-table* :table-type 'action) => (S 5)
;
;      (table-lookup 6 'F *goto-table* :table-type 'goto) => 3
;
;      (table-lookup 66 'F *goto-table* :table-type 'goto) => NIL
;
;      (table-lookup 6 nil *error-messages* :table-type 'error-message)
;         => "Missing id or left parenthesis"
;
;      (table-lookup 6 nil *productions* :table-type 'production) 
;         => (F -> ID)
;      
; ------------------------------------------------------------------------------

(defun table-lookup( state symbol table &key (table-type 'action) )

(let ((first-line-of-table (first table)))

;  Does this line contain the state we want?

(cond  ( (null table) nil)

       ( (element-of? state (first first-line-of-table))

;  If so, find the entry for the corresponding symbol.

         (cond ( (equal table-type 'error-message)

                     (first (second first-line-of-table)) )

               ( (equal table-type 'production)

                     (second first-line-of-table) )

               (t (list-lookup symbol (second first-line-of-table)
                               :table-type table-type))))

;  State wasn't found in the first line of the table.  Search the rest of the
;  table.

      ( t  (table-lookup state symbol (rest table) :table-type table-type))))
)





; ****************************** Parsing Functions *****************************

; ------------------------------------------------------------------------------
; |                                   shift!                                   |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Make one parsing shift move.
;
;  CALLING SEQUENCE
;
;      (shift! state-to-shift)
;
;      state-to-shift    State to be shifted onto the top of the stack.
;
;      Returns:          (SHIFT state-to-shift)
;                        We transfer one token from the input stack to the 
;                        parse stack and also append it to the old input stack.
;                        We also place state-to-shift on top of the parse stack.
;
;  EXAMPLE
;
;      (setq *parse-stack* '(0))
;      (setq *input-stack* '(id + [ id * id ] $))
;
;      (shift! 5) => (SHIFT 5)
;
;      *parse-stack* => (0 id 5)
;      *input-stack* => (+ [ id * id ] $)
;
; ------------------------------------------------------------------------------

(defun shift!( state-to-shift )

;  Shift one token from the input stack to the parse stack.
;  Save the token on the old input stack.
;  Pop this token from the input stack.

(setq *parse-stack* (rcons (first *input-stack*) *parse-stack*))

(setq *old-input-stack* (rcons (first *input-stack*) *old-input-stack*))

(setq *input-stack* (rest *input-stack*))


;  Shift the new state onto the parse stack.

(setq *parse-stack* (rcons state-to-shift *parse-stack*))

`(shift ,state-to-shift)
)




; ------------------------------------------------------------------------------
; |                                   reduce!                                  |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Make one parsing reduce move.
;
;  CALLING SEQUENCE
;
;      (reduce! production-number)
;
;      production-number  State to be shifted onto the top of the stack.
;
;      Returns:           (REDUCE production-number production)
;
;                         Pop twice the number of tokens in the right hand side
;                         of the production off the parse stack.
;
;                         Find out the goto state, then push the left hand side
;                         of the production and the goto state onto the parse
;                         stack.
;
;  EXAMPLE
;
;      (setq *parse-stack* '(0 id 5))
;      (setq *input-stack* '(id + [ id * id ] $))
;
;      (reduce! 6) => (REDUCE 6 (F -> ID))
;
;      *parse-stack* => (0 F 3)
;      *input-stack* => (ID + [ ID * ID ] $)
;
; ------------------------------------------------------------------------------

(defun reduce!( production-number )

;  Fetch the production.

(let* ( (production (table-lookup production-number nil *productions* 
                                  :table-type 'production))

;  Get the production's right hand side length and its left hand side
;  non-terminal.  If it is an epsilon production, A -> EPSILON, the
;  length is zero.

        (production-length 
           
            (if (equal (last production) '(EPSILON))

                     0
                     (length (nthcdr 2 production))))

        (non-term (first production)) 
        (goto-state nil)  )



;  Pop off the grammar symbols and states corresponding to the production.

    (setq *parse-stack* (reverse (nthcdr (* 2 production-length)
                                         (reverse *parse-stack*))))

;  Find out the goto state.

    (setq goto-state (table-lookup (rfirst *parse-stack*)
                                   non-term
                                   *goto-table*))

;  Push the non-terminal onto the parse stack.

    (setq *parse-stack* (rcons non-term *parse-stack*))


;  Push the goto state.

    (setq *parse-stack* (rcons goto-state *parse-stack*))


`(reduce ,production-number ,production))

)




; ------------------------------------------------------------------------------
; |                                 error-message                              |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Return an error message.
;
;  CALLING SEQUENCE
;
;      (error-message)
;
;      Returns:           (ERROR "error message")  
;                         The error message is based upon the current state on
;                         top of the stack.
;
;  EXAMPLE
;
;      (setq *parse-stack* '(0 E 1 + 6))
;
;      (error-message) => (ERROR "Missing id or left parenthesis")
;
; ------------------------------------------------------------------------------

(defun error-message()

(let ( (state (rfirst *parse-stack*)) )


;  Lookup the error message.
       
`(error ,(table-lookup state nil *error-messages* 
                       :table-type 'error-message)))
)




; ------------------------------------------------------------------------------
; |                                parse-one-step                              |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Make one parsing step.
;
;  CALLING SEQUENCE
;
;      (parse-one-step)
;
;      Returns:           (ACCEPT), (ERROR <error message>), (SHIFT state)
;                         or (REDUCE production-number production). 
;
;                         Make changes to *parse-stack*, *input-stack* and
;                         *old-input-stack* using the algorithm described
;                         under METHOD in the introduction.
;
;  EXAMPLE
;
;      (setq *parse-stack* '(0 id 5))
;      (setq *input-stack* '(id + [ id * id ] $))
;
;      (parse-one-step) => (REDUCE 6 (F -> ID))
;
;      *parse-stack* => (0 F 3)
;      *input-stack* => (ID + [ ID * ID ] $)
;
; ------------------------------------------------------------------------------

(defun parse-one-step()

;  Action from action table based on state on top of stack and lookahead.

(let ( (action (table-lookup (rfirst *parse-stack*)
                             (first  *input-stack*)
                             *action-table*)) )

    ; Based on the action, update the parse and input stacks.
    (cond ( (shift?  action) (shift!  (second action)))
          ( (reduce? action) (reduce! (second action)))
          ( (accept? action) '(accept))
          ( (error?  action) (error-message)))
)

)




; ********************************* Main program *******************************

; ------------------------------------------------------------------------------
; |                                   parser                                   |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Main program which parses a sentence in an LR(1) or LALR(1) grammar.
;
;  CALLING SEQUENCE
;
;      (parser parse-file in-file out-file)
;
;       parse-file    Name of file containing productions, action and goto
;                     tables.
;
;       in-file       Name of file containing the sentences to be parsed.
;
;       out-file      Parsing results.
;
;  EXAMPLE
;
;       See the files "parse-input.dat" and "parse-output.dat" for sample 
;       input and output.
;
; ------------------------------------------------------------------------------

(defun parser( parse-file in-file out-file)

(let ( (fp1 (open in-file  :direction :input))
       (fp2 (open out-file :direction :output :if-exists :supersede)) 
       (parse-action nil) 
       (raw-input nil) )

; Obligatory legal notice.
(print-legal-notice) 

(load-input-initialize-parser parse-file)

;  Parse each sentence in the input.

    (loop 

;  Exit upon end of file.

        (setq raw-input (read fp1 nil 'eof))

        (if (equal raw-input 'eof) (return))


; Read the next input sentence and append the end of input delimiter, $.

        (setq *input-stack* (rcons '$ raw-input))


;  Print an introductory header.

        (write-line (format nil "~%~%~%~A~S~%"
                                "Parsing the sentence: " raw-input) fp2)

        (write-line (format nil "~35A~20@A~3A~25A~%"
                                "PARSE STACK"
                                "INPUT STACK" "   "
                                "ACTION")          fp2)

        (setq *parse-stack*    '(0))
        (setq *old-input-stack* nil)


;  Parse each sentence.

        (loop 
 
            ;  Print the current parser configuration.
            (format fp2 "~35S~20@S~3A"
                                      *parse-stack*  
                                      *input-stack* "   ")

            ; One step of parsing, with updates to input and parse stacks.
            (setq parse-action (parse-one-step))


;  Print the parser action.  
(cond ( (equal (first parse-action) 'error)

              ; Declare error.
              (write-line (format nil "~25A~%" 
                                      "ERROR") fp2)

              ; Print the error message.
              (write-line (format nil "~A~%" (second parse-action)) fp2)
      )

      (t
              (write-line (format nil "~25S~%" parse-action) fp2))
)


;  Accept the sentence, or halt with error.

            (cond ( (equal (first parse-action) 'accept)

                        (write-line (format nil "~A~%" 
                                            "Sentence was grammatical.")
                                    fp2)
                        (fresh-line fp2)
                        (fresh-line fp2)
                        (return) )

                  ( (equal (first parse-action) 'error)

                        (write-line (format nil "~A~%" 
                                            "Sentence was not in the grammar.")
                                    fp2)
                        (fresh-line fp2)
                        (fresh-line fp2)
                        (return) ))))
            
    (close fp1)
    (close fp2))
)



; ------------------------------------------------------------------------------
; |                            parser-compile-all                              |
; ------------------------------------------------------------------------------
;
;  DESCRIPTION
;
;      Compile all the functions in this program, except parser-compile-all itself.
;
;  CALLING SEQUENCE
;
;      (parser-compile-all)
;
;  EXAMPLE
;
;      (parser-compile-all) =>
;
;      ;;; Compiling function LOAD-INPUT-AND-INITIALIZE...tail-merging...
;      assembling...emitting...done.
;
;          --- and so on, with pauses for garbage collection ---
;
;      ;;; Compiling function PARSER-GENERATOR...assembling...emitting...done
;      NIL
;
; ------------------------------------------------------------------------------

(defun parser-compile-all() 

;  Tell the compiler the following variables are global (have dynamic binding).

    (proclaim '(special *terminals*))
    (proclaim '(special *goto-graph*))
    (proclaim '(special *productions*))
    (proclaim '(special *action-table*))
    (proclaim '(special *goto-table*))
    (proclaim '(special *error-messages*))

    (proclaim '(special *input-stack*))
    (proclaim '(special *old-input-stack*))
    (proclaim '(special *parse-stack*))

(let ( (functions-to-compile

    '(load-input-initialize-parser

      element-of?  
      rfirst  
      rrest  
      rcons

      shift?
      reduce?  
      accept?  
      error?

      table-lookup  
      list-lookup

      shift!  
      reduce!  
      error-message

      parse-one-step              

      parser
      
      print-file-to-console
      file-exists?
      base-path!
      test-parser)))


;  Compile all the functions, except parser-compile-all itself.

(dolist (function-to-compile functions-to-compile)

    (compile function-to-compile)))
)


(defun component-present-p (value)
  (and value (not (eql value :unspecific))))

(defun directory-pathname-p  (p)
  (and
   (not (component-present-p (pathname-name p)))
   (not (component-present-p (pathname-type p)))
   p))

(defun pathname-as-directory (name)
  (let ((pathname (pathname name)))
    (when (wild-pathname-p pathname)
      (error "Can't reliably convert wild pathnames."))
    (if (not (directory-pathname-p name))
      (make-pathname
       :directory (append (or (pathname-directory pathname) (list :relative))
                          (list (file-namestring pathname)))
       :name      nil
       :type      nil
       :defaults pathname)
      pathname)))


; ------------------------------------------------------------------------------
; |                           file-exists?                                     |
; ------------------------------------------------------------------------------
;
; DESCRIPTION
;
;      Portable way to check if a file or directory exists.
;
; CALLING SEQUENCE
;
;      (file-exists? directory-or-file)
;
;      directory-or-file    Pathname for directory or file
;      Returns:             t if it is there, nil if not.
;
;
; EXAMPLES
;
;     (file-exists? "/NotThere") => nil
;     (file-exists? "/Volumes/seanoconnor") => t
;
; ------------------------------------------------------------------------------

(defun file-exists? (pathname)
  "Check if the file exists"
      #+(or sbcl lispworks openmcl)
      (probe-file pathname)

      #+(or allegro cmu)
      (or (probe-file (pathname-as-directory pathname))
                    (probe-file pathname))

      #+clisp
      (or (ignore-errors
           (probe-file (pathname-as-file pathname)))
                        (ignore-errors
                                  (let ((directory-form (pathname-as-directory pathname)))
                                              (when (ext:probe-directory directory-form)
                                                            directory-form))))

      #-(or sbcl cmu lispworks openmcl allegro clisp)
      (error "file-exists-p not implemented")
)



; ------------------------------------------------------------------------------
; |                               base-path!                                   |
; ------------------------------------------------------------------------------
;
; DESCRIPTION
;
;      Try to find out where the base directory for the web page is located.
;
; CALLING SEQUENCE
;
;      (base-path!)
;
;      Returns:             String of base path or nil if it can't find it.
;
;
; EXAMPLES
;
;     (base-path!) => "C:/Sean/WebSite"         ; Got it.
;     (base-path!) => nil                       ; Could't find it.
;
; ------------------------------------------------------------------------------

(defun base-path!()
    (let ( (possible-directories-list '( 
                                         "/cygdrive/c/Sean/WebSite"                 ; Windows / Cygwin
                                         "/Users/seanoconnor/Desktop/Sean/WebSite"  ; Mac OS
                                         "/home/seanoconnor/Desktop/Sean/WebSite"   ; Ubuntu Linux
                                        )))

     (dolist (base-path possible-directories-list)  
;       (format t "base path = ~S exists = ~S~%" base-path (file-exists? base-path) )
         (if (file-exists? base-path) (return (concatenate 'string base-path "/"))))
    )
)



; ------------------------------------------------------------------------------
; |                           test-parser                                      |
; ------------------------------------------------------------------------------
;
; DESCRIPTION
;
;     Run the parser on test input.
;
; CALLING SEQUENCE
;
;     (test-parser)
;
;      Set the files and paths to your requirements.  I'm assuming you've
;      installed cygwin if you're on a Windows machine.
;
; ------------------------------------------------------------------------------

(defun test-parser()

    ;  Compile all the functions for speed.
    (parser-compile-all)

    ;  Parse sentences using the parse tables.
    (let* ( 
            ; Set up the base directory paths.
            (base-path             (base-path!))
            (sub-path               "ComputerScience/Compiler/ParserGeneratorAndParser/")
            (parse-table-path      "ParseTables/")
            (sentence-path         "Sentences/" )

            ;  List the parse table files and sentences (inputs) and
            ;  parsed sentence files (output).
            (parse-table-file    '( "ParseTablesLALR(1)_S=SaSbEPSILON.dat"
                                    "ParseTablesLALR(1)_E=E+T_T.dat"
                                    "ParseTablesLALR(1)_Poly.dat" ) )
            (sentence-file       '( "SentencesS=SaSbEPSILON.dat"
                                    "SentencesE=E+T_T.dat"
                                    "SentencesPoly.dat" ) )
            (parsed-file         '( "ParsedSentencesLALR(1)S=SaSbEPSILON.dat"
                                    "ParsedSentencesLALR(1)E=E+T_T.dat"
                                    "ParsedSentencesLALR(1)Poly.dat") )
           )

           (dotimes (i (length parse-table-file))
               (let* (
                        ;  Create the full file path.
                        (full-parse-table-file  
                              (concatenate 'string 
                                           base-path sub-path parse-table-path 
                                           (nth i parse-table-file)) 
                        )

                        (full-sentence-file    
                              (concatenate 'string 
                                           base-path sub-path sentence-path 
                                           (nth i sentence-file))
                        )

                        (full-parsed-file     
                              (concatenate 'string 
                                           base-path sub-path sentence-path
                                           (nth i parsed-file))
                        )
                      )

                      ; Call the parser.
                      (parser full-parse-table-file full-sentence-file 
                              full-parsed-file)

                      ; Display the results to the console.
                      (print-file-to-console full-parsed-file)
                      (print-file-to-console full-sentence-file)
                      (print-file-to-console full-parsed-file)
               )
         )
    )
)
