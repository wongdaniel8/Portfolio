"""This module implements the core Scheme interpreter functions, including the
eval/apply mutual recurrence, environment model, and read-eval-print loop.
"""
from scheme_primitives import *
from scheme_reader import *
from ucb import main, trace

##############
# Eval/Apply #
##############


def scheme_eval(expr, env):
    """Evaluate Scheme expression EXPR in environment ENV. If ENV is None,
    simply returns EXPR as its value without further evaluation.
    >>> expr = read_line("(+ 2 2)")
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    scnum(4)
    """

    while env is not None:
        # Note: until extra-credit problem 22 is complete, env will
        # always be None on the second iteration of the loop, so that
        # the value of EXPR is returned at that point.

        if expr is None:
            raise SchemeError("Cannot evaluate an undefined expression.")

        # Evaluate Atoms
        if scheme_symbolp(expr):
            expr, env = env.lookup(expr).get_actual_value(), None
        elif scheme_atomp(expr):
            env = None

        # All non-atomic expressions are lists.
        elif not scheme_listp(expr):
            raise SchemeError("malformed list: {0}".format(str(expr)))
        else:
            first, rest = scheme_car(expr), scheme_cdr(expr)

            # Evaluate Combinations
            if (scheme_symbolp(first) # first might be unhashable
                and first in SPECIAL_FORMS):
                if proper_tail_recursion:
                    "*** YOUR CODE HERE ***"
                    expr, env = SPECIAL_FORMS[first](rest, env)
                    #expr, env = scheme_eval(expr, env), env #keep this? 

                else:
                    expr, env = SPECIAL_FORMS[first](rest, env)
                    expr, env = scheme_eval(expr, env), None
            else:
                procedure = scheme_eval(first, env)
                args = procedure.evaluate_arguments(rest, env)
                if proper_tail_recursion:
                    "*** YOUR CODE HERE ***"
                    expr,env= procedure.apply(args,env)

                else:
                    expr, env = scheme_apply(procedure,args, env), None 
                    


    return expr

#proper_tail_recursion = False
################################################################
# Uncomment the following line to apply tail call optimization #
################################################################
proper_tail_recursion = True

def scheme_apply(procedure, args, env):
    """Apply PROCEDURE (type Procedure) to argument values ARGS
    in environment ENV.  Returns the resulting Scheme value."""
    expr, env = procedure.apply(args, env)
    return scheme_eval(expr, env)

################
# Environments #
################

class Frame:
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent):
        """An empty frame with a PARENT frame (that may be None)."""
        self.bindings = {}
        self.parent = parent

    def __repr__(self):
        if self.parent is None:
            return "<Global Frame>"
        else:
            s = sorted('{0}: {1}'.format(k,v) for k,v in self.bindings.items())
            return "<{{{0}}} -> {1}>".format(', '.join(s), repr(self.parent))

    def __eq__(self, other):
        return isinstance(other, Frame) and \
                self.parent == other.parent

    def lookup(self, symbol):
        """Return the value bound to SYMBOL.  Errors if SYMBOL is not found.
        As a convenience, also accepts Python strings, which it turns into
        symbols."""
        if type(symbol) is str:
            symbol = intern(symbol)
        "*** YOUR CODE HERE ***"
        if symbol in self.bindings:
            return self.bindings[symbol]
        if self.parent!=None:
            return self.parent.lookup(symbol)
        raise SchemeError("unknown identifier: {0}".format(str(symbol)))


    def global_frame(self):
        """The global environment at the root of the parent chain."""
        e = self
        while e.parent is not None:
            e = e.parent
        return e

    def make_call_frame(self, formals, vals):
        """Return a new local frame whose parent is SELF, in which the symbols
        in the Scheme formal parameter list FORMALS are bound to the Scheme
        values in the Scheme value list VALS. Raise an error if too many or too
        few arguments are given.

        >>> env = create_global_frame()
        >>> formals, vals = read_line("(a b c)"), read_line("(1 2 3)")
        >>> env.make_call_frame(formals, vals)
        <{a: 1, b: 2, c: 3} -> <Global Frame>>
        """
        frame = Frame(self)
        "*** YOUR CODE HERE ***"
        if len(formals)!=len(vals):
            raise SchemeError("different number of arguments and parameters.")
        while len(formals)>0:
            frame.define(formals.first,vals.first)
            formals, vals = formals.second, vals.second
        return frame

    def define(self, sym, val):
        """Define Scheme symbol SYM to have value VAL in SELF.  As a
        convenience, SYM may be Python string, which is converted first
        to a Scheme symbol.  VAL must be a SchemeValue."""
        assert isinstance(val, SchemeValue), "values must be SchemeValues"
        if type(sym) is str:
            sym = intern(sym)
        self.bindings[sym] = val

#####################
# Procedures        #
#####################

class Procedure(SchemeValue):
    """The superclass of all kinds of procedure in Scheme."""

    # Arcane Technical Note: The odd placement of the import from scheme in
    # evaluate_arguments is necessary because it introduces mutually recursive
    # imports between this file and scheme.py.  The effect of putting it
    # here is that we delay attempting to access scheme.scheme_eval until
    # after the scheme module's initialization is finished.

    def evaluate_arguments(self, arg_list, env):
        """Evaluate the expressions in ARG_LIST in ENV to produce
        arguments for this procedure. Default definition for procedures."""
        from scheme import scheme_eval
        return arg_list.map(lambda operand: scheme_eval(operand, env))

class PrimitiveProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False):
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[primitive]'

    def __repr__(self):
        return "PrimitiveProcedure({})".format(str(self))

    def apply(self, args, env):
        """Apply a primitive procedure to ARGS in ENV.  Returns
        a pair (val, None), where val is the resulting value.
        >>> twos = Pair(SchemeInt(2), Pair(SchemeInt(2), nil))
        >>> plus = PrimitiveProcedure(scheme_add, False)
        >>> plus.apply(twos, None)
        (scnum(4), None)
        """
        "*** YOUR CODE HERE ***"
        mylist=[]
        while args!=nil:
            mylist.append(args.first)
            args=args.second
        if self.use_env:
            mylist.append(env) 
        try:
            x=self.fn(*mylist)
        except TypeError:
            raise SchemeError('SchemeError')
        return (x,None)  




class LambdaProcedure(Procedure):
    """A procedure defined by a lambda expression or the complex define form."""

    def __init__(self, formals, body, env = None):
        """A procedure whose formal parameter list is FORMALS (a Scheme list),
        whose body is the single Scheme expression BODY, and whose parent
        environment is the Frame ENV.  A lambda expression containing multiple
        expressions, such as (lambda (x) (display x) (+ x 1)) can be handled by
        using (begin (display x) (+ x 1)) as the body."""
        self.formals = formals
        self.body = body
        self.env = env

    def _symbol(self):
        return 'lambda'

    def __str__(self):
        return "({0} {1} {2})".format(self._symbol(),
                                      str(self.formals), str(self.body))

    def __repr__(self):
        args = (self.formals, self.body, self.env)
        return "{0}Procedure({1}, {2}, {3})".format(self._symbol().capitalize(),
                                                    *(repr(a) for a in args))

    def __eq__(self, other):
        return type(other) is type(self) and \
               self.formals == other.formals and \
               self.body == other.body and \
               self.env == other.env

    def apply(self, args, env):
        if proper_tail_recursion:
            # Implemented in Question 22.
            "*** YOUR CODE HERE ***"
            frame = Frame.make_call_frame(self.env,self.formals,args)
            return self.body, frame 

        else:
            "*** YOUR CODE HERE ***"
            
            frame = Frame.make_call_frame(self.env,self.formals,args)
            x=scheme_eval(self.body,frame)
            return x, None


class MuProcedure(LambdaProcedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """

    def _symbol(self):
        return 'mu'

    def apply(self, args, env):
        if proper_tail_recursion:
            # Implemented in Question 22.
            "*** YOUR CODE HERE ***"
            frame=Frame.make_call_frame(env,self.formals,args)
            return self.body,frame 

        else:
            "*** YOUR CODE HERE ***"
            frame=Frame.make_call_frame(env,self.formals,args)
            x=scheme_eval(self.body,frame)
            return x, None 

# Call-by-name (nu) extension.
class NuProcedure(LambdaProcedure):
    """A procedure whose parameters are to be passed by name."""

    def _symbol(self):
        return 'nu'

    "*** YOUR CODE HERE ***"
    def apply(self,args,env):
        frame=Frame.make_call_frame(env,self.formals,args)
        return self.body,frame
        
    

    def evaluate_arguments(self, arg_list, env):
        from scheme import scheme_eval
        return arg_list.map(lambda operand: Thunk(operand,env))



class Thunk(LambdaProcedure):
    """A by-name value that is to be called as a parameterless function when
    its value is fetched to be used."""

    "*** YOUR CODE HERE ***"
    def __symbol__(self):
        return 'thunk'

    def __init__(self,value,env):
        LambdaProcedure.__init__(self,None,None,env)
        self.value=value

    def get_actual_value(self):
        return scheme_eval(self.value,self.env).get_actual_value()





#################
# Special forms #
#################

# All of the 'do_..._form' methods return a value and an environment,
# as for the 'apply' method on Procedures.  That is, they either return
# (V, None), indicating that the value of the special form is V, or they
# return (Expr, Env), indicating that the value of the special form is what
# you would get by evaluating Expr in the environment Env.

def do_lambda_form(vals, env, function_type=LambdaProcedure):
    """Evaluate a lambda form with formals VALS[0] and body VALS.second
    in environment ENV, creating a procedure of type FUNCTION_TYPE
    (a subtype of Procedure)."""
    check_form(vals, 2)
    formals = vals[0]
    check_formals(formals)
    "*** YOUR CODE HERE ***"
    if len(vals) > 2:
        body = Pair('begin', vals.second)
    else:
        body = vals.second.first
    return function_type(formals, body, env), None
    



def do_mu_form(vals, env):
    """Evaluate a mu (dynamically scoped lambda) form with formals VALS[0]
    and body VALS.second in environment ENV."""
    return do_lambda_form(vals, env, function_type=MuProcedure)

def do_nu_form(vals, env):
    """Evaluate a mu (call-by-name scoped lambda) form with formals VALS[0]
    and body VALS.second in environment ENV."""
    return do_lambda_form(vals, env, function_type=NuProcedure)

def do_define_form(vals, env):
    """Evaluate a define form with parameters VALS in environment ENV."""
    check_form(vals, 2)
    target = vals[0]
    if scheme_symbolp(target):
        check_form(vals, 2, 2)
        "*** YOUR CODE HERE ***"
        env.define(target, scheme_eval(vals[1], env) )
        return (target,None)
        
    elif scheme_pairp(target):
        "*** YOUR CODE HERE ***"
       
        if scheme_symbolp(vals[0].first):
            vals_express=Pair(vals[0].second,vals.second)
            evaluation=do_lambda_form(vals_express,env)[0]

            env.define(vals[0].first,evaluation)
            return (vals[0].first, None)
        else:
            raise SchemeError()


    else:
        raise SchemeError("bad argument to define")


def do_quote_form(vals, env):
    """Evaluate a quote form with parameters VALS. ENV is ignored."""
    check_form(vals, 1, 1)
    "*** YOUR CODE HERE ***"
    return (vals[0],None)


def do_let_form(vals, env):
    """Evaluate a let form with parameters VALS in environment ENV."""
    check_form(vals, 2)
    bindings = vals[0]
    exprs = vals.second
    if not scheme_listp(bindings):
        raise SchemeError("bad bindings list in let form")

    # Add a frame containing bindings
    names, values = nil, nil
    "*** YOUR CODE HERE ***"

    for name,value in bindings:
        names=Pair(name,names)
        values=Pair(scheme_eval(value,env),values)
    new_env = Frame.make_call_frame(env,names,values)


    # Evaluate all but the last expression after bindings, and return the last
    last = len(exprs)-1
    for i in range(0, last):
        scheme_eval(exprs[i], new_env)
    return exprs[last], new_env


#########################
# Logical Special Forms #
#########################

def do_if_form(vals, env):
    """Evaluate if form with parameters VALS in environment ENV."""
    check_form(vals, 2, 3)
    "*** YOUR CODE HERE ***"

    if scheme_eval(vals[0],env):
        return scheme_eval(vals[1],env),None
    if len(vals)==2 and not scheme_eval(vals[0],env):
        return okay,None 
    return scheme_eval(vals[2],env),None
    

def do_and_form(vals, env):
    """Evaluate short-circuited and with parameters VALS in environment ENV."""
    "*** YOUR CODE HERE ***"


    if len(vals)==0:
        return scheme_true,None 
        
    for op in range(0,len(vals)-1): 
        if not scheme_eval(vals[op],env):
            return scheme_false,None  
    return scheme_eval(vals[len(vals)-1],env),None  
    
    


def quote(value):
    """Return a Scheme expression quoting the Scheme VALUE.

    >>> s = quote('hello')
    >>> print(s)
    (quote hello)
    >>> scheme_eval(s, Frame(None))  # "hello" is undefined in this frame.
    intern('hello')
    """
    return Pair("quote", Pair(value, nil))

def do_or_form(vals, env):
    """Evaluate short-circuited or with parameters VALS in environment ENV."""
    "*** YOUR CODE HERE ***"
 
    if len(vals)==0:
        return scheme_false,None 
    for op in range(0,len(vals)-1):
        x=scheme_eval(vals[op],env)
        if x:
            return x, None
    return scheme_eval(vals[len(vals)-1],env),None

def do_cond_form(vals, env):
    """Evaluate cond form with parameters VALS in environment ENV."""
    num_clauses = len(vals)
    for i, clause in enumerate(vals):
        check_form(clause, 1)
        if clause.first is else_sym:
            if i < num_clauses-1:
                raise SchemeError("else must be last")
            test = scheme_true
            if clause.second is nil:
                raise SchemeError("badly formed else clause")
        else:
            test = scheme_eval(clause.first, env)
        if test:
            "*** YOUR CODE HERE ***"
            if len(clause.second)==1:
                return clause.second.first,env
            if len(clause)>=2:
                return do_begin_form(clause.second,env) 
            return test,None            
    return okay, None

def do_begin_form(vals, env):
    """Evaluate begin form with parameters VALS in environment ENV."""
    check_form(vals, 0)
    if scheme_nullp(vals):
        return okay, None
    "*** YOUR CODE HERE ***"
    last_one=vals[len(vals)-1]
    for index in range(0,len(vals)-1):
        scheme_eval(vals[index],env)
    return (scheme_eval(last_one,env),None)

    

# Collected symbols with significance to the interpreter

and_sym              = intern("and")
begin_sym            = intern("begin")
cond_sym             = intern("cond")
define_macro_sym     = intern("define-macro")
define_sym           = intern("define")
else_sym             = intern("else")
if_sym               = intern("if")
lambda_sym           = intern("lambda")
let_sym              = intern("let")
mu_sym               = intern("mu")
nu_sym               = intern("nu")
or_sym               = intern("or")
quasiquote_sym       = intern("quasiquote")
quote_sym            = intern("quote")
set_bang_sym         = intern("set!")
unquote_splicing_sym = intern("unquote-splicing")
unquote_sym          = intern("unquote")

# Collected special forms

SPECIAL_FORMS = {
        and_sym:          do_and_form,
        begin_sym:        do_begin_form,
        cond_sym:         do_cond_form,
        define_sym:       do_define_form,
        if_sym:           do_if_form,
        lambda_sym:       do_lambda_form,
        let_sym:          do_let_form,
        mu_sym:           do_mu_form,
        nu_sym:           do_nu_form,
        or_sym:           do_or_form,
        quote_sym:        do_quote_form,
}

# Utility methods for checking the structure of Scheme programs

def check_form(expr, min, max = None):
    """Check EXPR (default SELF.expr) is a proper list whose length is
    at least MIN and no more than MAX (default: no maximum). Raises
    a SchemeError if this is not the case."""
    if not scheme_listp(expr):
        raise SchemeError("badly formed expression: " + str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError("too few operands in form")
    elif max is not None and length > max:
        raise SchemeError("too many operands in form")

def check_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of formals
    is not a well-formed list of symbols or if any symbol is repeated.

    >>> check_formals(read_line("(a b c)"))
    """
    "*** YOUR CODE HERE ***"
    list_of_symbols=[]
    for ar in formals:
        if ar in list_of_symbols:
            raise SchemeError()
        list_of_symbols.append(ar)
        if not scheme_symbolp(ar):
            raise SchemeError()



################
# Input/Output #
################

def read_eval_print_loop(next_line, env, quiet=False, startup=False,
                         interactive=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(scstr(filename), True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    scheme_print(result)
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in err.args[0]):
                raise
            print("Error:", err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print("\nKeyboardInterrupt")
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            return


def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or (SYM,
    QUIET, ENV). The file named SYM is loaded in environment ENV, with verbosity
    determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        vals = args[:-1]
        raise SchemeError("wrong number of arguments to load: {0}".format(vals))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = intern(str(sym))
    check_type(sym, scheme_symbolp, 0, "load")
    with scheme_open(str(sym)) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)
    read_eval_print_loop(next_line, env.global_frame(), quiet=quiet)
    return okay

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define("eval", PrimitiveProcedure(scheme_eval, True))
    env.define("apply", PrimitiveProcedure(scheme_apply, True))
    env.define("load", PrimitiveProcedure(scheme_load, True))

    for names, fn in get_primitive_bindings():
        for name in names:
            proc = PrimitiveProcedure(fn)
            env.define(name, proc)
    return env

@main
def run(*argv):
    next_line = buffer_input
    interactive = True
    load_files = ()
    if argv:
        try:
            filename = argv[0]
            if filename == '-load':
                load_files = argv[1:]
            else:
                input_file = open(argv[0])
                lines = input_file.readlines()
                def next_line():
                    return buffer_lines(lines)
                interactive = False
        except IOError as err:
            print(err)
            sys.exit(1)
    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()