#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import os
import re
import getopt
import shlex
import inspect
import getpass
import socket


USAGE = "Usage: %s [options]" % sys.argv[0] + """
Options:     -h, --help      Display this help message and exit
"""

def usage(msg=''):
    """Print usage information to stderr.

    @param msg: An optional message that will be displayed before the usage
    @return: None
    """
    if msg:
        print >> sys.stderr, msg
    print >> sys.stderr, USAGE

class ColourFunctions(object):
    NAME_KEY = 0
    CODE_KEY = 1
    VAL_KEY  = 2
    
    # Colour names
    BLACK   = {NAME_KEY : "black",   CODE_KEY : "k", VAL_KEY : 0}
    RED     = {NAME_KEY : "red",     CODE_KEY : "r", VAL_KEY : 1}
    GREEN   = {NAME_KEY : "green",   CODE_KEY : "g", VAL_KEY : 2}
    YELLOW  = {NAME_KEY : "yellow",  CODE_KEY : "y", VAL_KEY : 3}
    BLUE    = {NAME_KEY : "blue",    CODE_KEY : "b", VAL_KEY : 4}
    MAGENTA = {NAME_KEY : "magenta", CODE_KEY : "m", VAL_KEY : 5}
    CYAN    = {NAME_KEY : "cyan",    CODE_KEY : "c", VAL_KEY : 6}
    WHITE   = {NAME_KEY : "white",   CODE_KEY : "w", VAL_KEY : 7}
    COLOURS = [BLACK,RED,GREEN,YELLOW,BLUE,MAGENTA,CYAN,WHITE]
    
    # Prefixes
    FG_PREFIX   = {NAME_KEY : "foreground",     CODE_KEY : "fg",    VAL_KEY : "0;3"}  # Foreground
    BG_PREFIX   = {NAME_KEY : "background",     CODE_KEY : "bg",    VAL_KEY : "4"}    # Background
    EM_PREFIX   = {NAME_KEY : "bold",           CODE_KEY : "b",     VAL_KEY : "1;3"}  # Bold
    UL_PREFIX   = {NAME_KEY : "underline",      CODE_KEY : "u",     VAL_KEY : "4;3"}  # Underline
    HIFG_PREFIX = {NAME_KEY : "hi_foreground",  CODE_KEY : "hifg",  VAL_KEY : "0;9"}  # High Intensity Foreground
    HIBG_PREFIX = {NAME_KEY : "hi_background",  CODE_KEY : "hibg",  VAL_KEY : "0;10"} # High Intensity Background
    HIEM_PREFIX = {NAME_KEY : "hi_bold",        CODE_KEY : "hib",   VAL_KEY : "1;9"}  # High Intensity Bold
    PREFIXES = [FG_PREFIX,BG_PREFIX,EM_PREFIX,UL_PREFIX,HIFG_PREFIX,HIBG_PREFIX,HIEM_PREFIX]

    RESET_KEY       = 0
    NOCOUNT_START   = "\001"
    NOCOUNT_END     = "\002"
    ESCAPE_CHAR     = "\033["
    END_CODE        = "m"


    def _encode(self, code, wrap=True):
        s = ColourFunctions.ESCAPE_CHAR+\
                str(code)+\
                ColourFunctions.END_CODE
        if wrap:
            s = ColourFunctions.NOCOUNT_START+\
                s+\
                ColourFunctions.NOCOUNT_END
        return s

    def startColour(self, colour, prefix=FG_PREFIX, wrap=True):
        col = self._getColourObj(colour)
        pre = self._getPrefixObj(prefix)
        return self._encode("%s%s" % (str(pre[self.VAL_KEY]), str(col[self.VAL_KEY])), wrap=wrap)
    
    def stopColour(self, wrap=True):
        return self._encode(self.RESET_KEY, wrap=wrap)

    def _getColourObj(self,identifier):
        # Is it a colour dict?
        if identifier in self.COLOURS:
            return identifier
        
        # Is it a name key?
        for colour in self.COLOURS:
            if identifier == colour[self.NAME_KEY]:
                return colour

        # Is it a code key?
        for colour in self.COLOURS:
            if identifier == colour[self.CODE_KEY]:
                return colour
            
        raise KeyError("No such colour %s" % str(identifier))

    def _getPrefixObj(self, identifier):
        # Is it a prefix dict?
        if identifier in self.PREFIXES:
            return identifier
        
        # Is it a name key?
        for prefix in self.PREFIXES:
            if identifier == prefix[self.NAME_KEY]:
                return prefix

        # Is it a code key?
        for prefix in self.PREFIXES:
            if identifier == prefix[self.CODE_KEY]:
                return prefix
            
        raise KeyError("No such prefix %s" % str(identifier))

    @staticmethod
    def _colourFuncFactory(cls, colour):
        def func(self, literal, prefix=cls.FG_PREFIX):
            #function_name = inspect.stack()[0][3]
            return self.startColour(colour,prefix) + literal + self.stopColour()
        return func
    
    @staticmethod
    def _populateClassFunctions(cls):
        for colour in cls.COLOURS:
            colourName = colour[cls.NAME_KEY]
            setattr(cls, colourName, cls._colourFuncFactory(cls, colourName))


    def __new__(cls, *args, **kwargs):
        # Add the new instance methods to the 
        # class object before instantiating it
        cls._populateClassFunctions(cls)
        
        # Instantiate the new class and return it
        return object.__new__(cls, *args, **kwargs)


class Lexer(shlex.shlex):
    def __init__(self, instream):
        shlex.shlex.__init__(self, instream=instream.replace('\n','\n\n'))
        self.wordchars = self.wordchars + r":;#~@-_=+*/?'!$^&()|<>.," + '"'
        self.commenters = '%'

class Parser(object):
    @staticmethod
    def _guardedNext(lex):
        token = None
        try:
            token = lex.next()
        except StopIteration:
            pass
        return token
    
    def _atom(self, lex, token):
        out = []
        while True:
            try:
                if token == '\\':
                    # Function
                    name = lex.next()
                    args = []
                    optargs = []
                    token = self._guardedNext(lex)
                    while token in ['{', '[']:
                        # Arguments
                        arg = self._atom(lex, lex.next())

                        if token == '{':
                            args.append(arg)
                        elif token == '[':
                            optargs.append(arg)
                        token = self._guardedNext(lex)
                    func = {'type': 'function', 'name': name}
                    if args:
                        func['args'] = args
                    if optargs:
                        func['optargs'] = optargs
                    out.append(func)
                    if token is None:
                        raise StopIteration
                elif token in ['}',']']:
                    # End scope
                    break
                else:
                    # String literal
                    out.append({ 'type': 'literal', 'value': token})
                    token = lex.next()
            except StopIteration:
                break
        return out
    
    def parse(self, instream):
        self.lex = Lexer(instream)
        return self._atom(self.lex, self.lex.next())


class Compiler(object):
    def __init__(self, status=None):
        if status is None:
            status = Status()
            
        self.status = status
        self.funcs = FunctionContainer(status)

    def compile(self, parsedStruct):
        out = ""
        for element in parsedStruct:
            if element['type'] == 'literal':
                # Literals go to the output verbatim
                out += element['value']
            elif element['type'] == 'function':
                # First arg is the function name
                args = [element['name']]
                # Then the required arguments
                if 'args' in element:
                    for arg in element['args']:
                        args.append(self.compile(arg))
                # Finally any optional arguments
                if 'optargs' in element:
                    for optarg in element['optargs']:
                        args.append(self.compile(optarg))
                # Call the function!
                out += str(self.funcs._call(*args))
                
        return out

class StandardFunctions(object):

#               \a     an ASCII bell character (07)
#               \d     the date in "Weekday Month Date" format (e.g., "Tue May 26")
#               \D{format}
#                      the format is passed to strftime(3) and the result is inserted into
#                      the  prompt  string;  an  empty format results in a locale-specific
#                      time representation.  The braces are required
#               \e     an ASCII escape character (033)
#              x\h     the hostname up to the first `.'
#              x\H     the hostname
#               \j     the number of jobs currently managed by the shell
#               \l     the basename of the shell's terminal device name
#              x\n     newline
#              x\r     carriage return
#               \s     the name of the shell, the basename of $0  (the  portion  following
#                      the final slash)
#               \t     the current time in 24-hour HH:MM:SS format
#               \T     the current time in 12-hour HH:MM:SS format
#               \@     the current time in 12-hour am/pm format
#               \A     the current time in 24-hour HH:MM format
#              x\u     the username of the current user
#               \v     the version of bash (e.g., 2.00)
#               \V     the release of bash, version + patch level (e.g., 2.00.0)
#              x\w     the  current working directory, with $HOME abbreviated with a tilde
#                      (uses the value of the PROMPT_DIRTRIM variable)
#              x\W     the basename of the current working directory, with $HOME  abbreviated with a tilde
#               \!     the history number of this command
#               \#     the command number of this command
#              x\$     if the effective UID is 0, a #, otherwise a $
#               \nnn   the character corresponding to the octal number nnn
#               \\     a backslash
#              x\[     begin a sequence of non-printing characters, which could be used to
#                      embed a terminal control sequence into the prompt
#              x\]     end a sequence of non-printing characters


    def space(self):
        return r" "
    
    def newline(self):
        return r"\n"

    def carriagereturn(self):
        return r"\r"

    def user(self):
        return getpass.getuser()

    def hostname(self):
        return socket.gethostname().split(".")[0]

    def hostnamefull(self):
        return socket.gethostname()

    def workingdir(self):
        home = os.path.expanduser(r"~")
        cwd = os.getcwd()
        return re.sub(r'^%s' % home, r"~", cwd)

    def workingdirbase(self):
        return os.path.basename(os.getcwd())

    def dollar(self, euid=None):
        if euid is None:
            euid = os.geteuid()
        if int(euid) == 0:
            return r"#"
        else:
            return r"$"

class ExpressionFunctions(object):
    @staticmethod
    def _tobool(expr):
        if str(expr).lower() in ['true', '1', 't', 'y', 'yes']:
            return True
        else:
            return False
    
    def equals(self, a,b):
        return a == b

    def ifexpr(self, cond,thenval,elseval=None):
        if ExpressionFunctions._tobool(cond):
            return thenval
        else:
            if elseval:
                return elseval
            else:
                return ""

    def exitsuccess(self):
        if self.status.exitCode == 0:
            return True
        else:
            return False


class FunctionContainer(object):

    def lower(self, literal):
        return str(literal).lower()

    def greater(self, a,b):
        if a > b:
            return a
        else:
            return b

    def join(self, *args):
        if len(args) < 1:
            raise TypeError("join needs at least one argument")
        delim = args[0]
        args = args[1:]
        return str(delim).join(args)


    def _call(self, *args):
        if len(args) < 1:
            raise TypeError("call requires a name")
        name = args[0]
        args = args[1:]
        return self.functions[name](*args)
    
    def _addFunctions(self, obj):
        objName = "obj" + obj.__class__.__name__
        setattr(self, objName, obj)
        obj.status = self.status
        for name, func in inspect.getmembers(obj, inspect.ismethod):
            if name[0] != "_":
                self.functions[name] = func
    
    def __init__(self, status=None):
        if status is None:
            status = Status()
        self.status = status
        self.functions = {}
        self._addFunctions(self)
        for cls in [StandardFunctions, ExpressionFunctions, ColourFunctions]:
            self._addFunctions(cls())



class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.parser = Parser()
        self.compiler = Compiler(status)


    def getPrompt(self):
        return self.compiler.compile(self.parser.parse(
            r"""
            \green{
                \user
            }
            @
            \hostname
            \space
            \blue[bold]{
                \workingdir
            }
            \space
            \dollar
            \space
            """
        ))


class Status(object):
    def __init__(self, exitCode=0):
        self.exitCode = exitCode

def main(argv=None):
    """Main function. This is the entry point for the program and is run when
    the script is executed stand-alone (i.e. not included as a module

    @param argv: A list of argumets that can over-rule the command line arguments.
    @return: Error status
    @rtype: int
    """
    # Use the command line (system) arguments if none were passed to main
    if argv is None:
        argv = sys.argv


    # Parse command line options
    try:
        opts, args = getopt.getopt(argv[1:], "hbc", ["help", "bash", "colours"])
    except getopt.error, msg:
        usage(msg)
        return 1

    # Defaults

    # Act upon options
    for option, arg in opts:
        if option in ("-h","--help"):
            usage()
            return 0

        if option in ("-b", "--bash"):
            print "export PS1=\"\\$(%s \\$?)\"" % sys.argv[0]
            return 0

        if option in ("-c", "--colours"):
            for prefix in ColourFunctions.PREFIXES:
                for colour in ColourFunctions.COLOURS:
                    print "%s%s : %s%s" % (ColourFunctions.startColour(colour, prefix, False), 
                                           prefix[ColourFunctions.NAME_KEY], 
                                           colour[ColourFunctions.NAME_KEY], 
                                           ColourFunctions.stopColour(False))
            return 0

    if len(args) < 1:
        usage("Not enough arguments")
        return 1

    exitStatus = argv[1]

    s = Status(exitStatus)

    p = Prompt(s)
    sys.stdout.write(p.getPrompt())

    return 0




#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
# Run main if this file is not imported as a module
if __name__ == "__main__":
    sys.exit(main())
