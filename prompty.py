#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import getopt
import shlex


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

class Colour(object):
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
    NOCOUNT_START   = "\["
    NOCOUNT_END     = "\]"
    ESCAPE_CHAR     = "\033["
    END_CODE        = "m"

    @staticmethod
    def _encode(code, wrap=True):
        s = Colour.ESCAPE_CHAR+\
                str(code)+\
                Colour.END_CODE
        if wrap:
            s = Colour.NOCOUNT_START+\
                s+\
                Colour.NOCOUNT_END
        return s

    @staticmethod
    def startColour(colour, prefix=FG_PREFIX, wrap=True):
        col = Colour._getColourObj(colour)
        pre = Colour._getPrefixObj(prefix)
        return Colour._encode("%s%s" % (str(pre[Colour.VAL_KEY]), str(col[Colour.VAL_KEY])), wrap=wrap)
    
    @staticmethod
    def stopColour(wrap=True):
        return Colour._encode(Colour.RESET_KEY, wrap=wrap)

    @staticmethod
    def _getColourObj(identifier):
        # Is it a colour dict?
        if identifier in Colour.COLOURS:
            return identifier
        
        # Is it a name key?
        for colour in Colour.COLOURS:
            if identifier == colour[Colour.NAME_KEY]:
                return colour

        # Is it a code key?
        for colour in Colour.COLOURS:
            if identifier == colour[Colour.CODE_KEY]:
                return colour
            
        raise KeyError("No such colour %s" % str(identifier))

    @staticmethod
    def _getPrefixObj(identifier):
        # Is it a prefix dict?
        if identifier in Colour.PREFIXES:
            return identifier
        
        # Is it a name key?
        for prefix in Colour.PREFIXES:
            if identifier == prefix[Colour.NAME_KEY]:
                return prefix

        # Is it a code key?
        for prefix in Colour.PREFIXES:
            if identifier == prefix[Colour.CODE_KEY]:
                return prefix
            
        raise KeyError("No such prefix %s" % str(identifier))


class Lexer(shlex.shlex):
    def __init__(self, instream):
        shlex.shlex.__init__(self, instream=instream)
        self.wordchars = self.wordchars + r":;#~@-_=+*/?'!$^&()|<>" + '"'
        self.commenters = '%'

class Parser(object):
    def parse(self, instream):
        return instream


class Prompt(object):

    
    def __init__(self):
        pass

    def startColour(self, col):
        pass

    def getPrompt(self):
        # Something like this?
        # "\green{\user}@\hostname \blue[bold]{workingdir} \$ "
        return Colour.startColour("green") + "\u" + Colour.stopColour() + "@\h " + Colour.startColour("blue","b") + "\w" + Colour.stopColour() + " \$ "


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
            print "export PS1=\"$(%s)\"" % sys.argv[0]
            return 0

        if option in ("-c", "--colours"):
            for prefix in Colour.PREFIXES:
                for colour in Colour.COLOURS:
                    print "%s%s : %s%s" % (Colour.startColour(colour, prefix, False), 
                                           prefix[Colour.NAME_KEY], 
                                           colour[Colour.NAME_KEY], 
                                           Colour.stopColour(False))
            return 0

    #if len(args) < 0:
    #    usage("Not enough arguments")
    #    return 1


    p = Prompt()
    sys.stdout.write(p.getPrompt())

    return 0




#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
# Run main if this file is not imported as a module
if __name__ == "__main__":
    sys.exit(main())
