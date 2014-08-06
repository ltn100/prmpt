#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys

NAME_KEY = 0
CODE_KEY = 1
VAL_KEY  = 2

# \e[x;yy;zz
# x = prefix
# yy = 

# Colour names
BLACK   = {NAME_KEY : "black",      CODE_KEY : "k",     VAL_KEY : 0}
RED     = {NAME_KEY : "red",        CODE_KEY : "r",     VAL_KEY : 1}
GREEN   = {NAME_KEY : "green",      CODE_KEY : "g",     VAL_KEY : 2}
YELLOW  = {NAME_KEY : "yellow",     CODE_KEY : "y",     VAL_KEY : 3}
BLUE    = {NAME_KEY : "blue",       CODE_KEY : "b",     VAL_KEY : 4}
MAGENTA = {NAME_KEY : "magenta",    CODE_KEY : "m",     VAL_KEY : 5}
CYAN    = {NAME_KEY : "cyan",       CODE_KEY : "c",     VAL_KEY : 6}
LGREY   = {NAME_KEY : "lightgrey",  CODE_KEY : "lg",    VAL_KEY : 7}
DGREY   = {NAME_KEY : "darkgrey",   CODE_KEY : "dg",    VAL_KEY : 60}
LRED    = {NAME_KEY : "lightred",   CODE_KEY : "lr",    VAL_KEY : 61}
LGREEN  = {NAME_KEY : "lightgreen", CODE_KEY : "lgn",   VAL_KEY : 62}
LYELLOW = {NAME_KEY : "lightyellow",CODE_KEY : "ly",    VAL_KEY : 63}
LBLUE   = {NAME_KEY : "lightblue",  CODE_KEY : "lb",    VAL_KEY : 64}
LMAGENTA= {NAME_KEY : "lightmagenta",CODE_KEY :"lm",    VAL_KEY : 65}
LCYAN   = {NAME_KEY : "lightcyan",  CODE_KEY : "lc",    VAL_KEY : 66}
WHITE   = {NAME_KEY : "white",      CODE_KEY : "w",     VAL_KEY : 67}
COLOURS = [BLACK,RED,GREEN,YELLOW,BLUE,MAGENTA,CYAN,LGREY,
           DGREY,LRED,LGREEN,LYELLOW,LBLUE,LMAGENTA,LCYAN,WHITE]

FG_OFFSET = 30
BG_OFFSET = 40

# Prefixes
NORMAL      = {NAME_KEY : "normal",     CODE_KEY : "n",     VAL_KEY : 0}
BOLD        = {NAME_KEY : "bold",       CODE_KEY : "b",     VAL_KEY : 1}
DIM         = {NAME_KEY : "dim",        CODE_KEY : "d",     VAL_KEY : 2}
ITALIC      = {NAME_KEY : "italic",     CODE_KEY : "i",     VAL_KEY : 3}
UNDERLINE   = {NAME_KEY : "underline",  CODE_KEY : "u",     VAL_KEY : 4}
BLINK       = {NAME_KEY : "blink",      CODE_KEY : "bl",    VAL_KEY : 5}
INVERTED    = {NAME_KEY : "inverted",   CODE_KEY : "in",    VAL_KEY : 7}

PREFIXES = [NORMAL,BOLD,DIM,ITALIC,UNDERLINE,BLINK,INVERTED]

RESET_KEY       = 0
NOCOUNT_START   = u"\001"
NOCOUNT_END     = u"\002"
ESCAPE_CHAR     = u"\033["
END_CODE        = u"m"


def _encode(code, wrap=True):
    """
    Add the bash escape codes for colours
    i.e.: \e[CODEm
    
    :param wrap: Wrap the code in additional characters
                 to signify non-printing characters are
                 contained
    """
    s = ESCAPE_CHAR+\
            unicode(code)+\
            END_CODE
    if wrap:
        s = NOCOUNT_START+\
            s+\
            NOCOUNT_END
    return s


def _get8bitColourObj(identifier):
    raise ValueError

def _get24bitColourObj(identifier):
    raise ValueError

def _getColourObj(identifier):
    if isinstance(identifier, dict):
        # Is it a colour dict?
        if identifier in COLOURS:
            return identifier
    else:
        # Assume identifier is a sting
        if len(identifier) == 0:
            raise KeyError("No such colour %s" % str(identifier))
        
        # Is it a name key?
        for colour in COLOURS:
            if identifier == colour[NAME_KEY]:
                return colour
    
        # Is it a code key?
        for colour in COLOURS:
            if identifier == colour[CODE_KEY]:
                return colour
        
        # Look for a colour code
        try:
            # 8-bit colour code
            colour = _get8bitColourObj(identifier)
            return colour
        except ValueError:
            try:
                # 24-bit colour code
                colour = _get24bitColourObj(identifier)
                return colour
            except ValueError:
                pass
        
    raise KeyError("No such colour %s" % str(identifier))


def _getPrefixObj(identifier):
    # Is it a prefix dict?
    if identifier in PREFIXES:
        return identifier
    
    # Is it a name key?
    for prefix in PREFIXES:
        if identifier == prefix[NAME_KEY]:
            return prefix

    # Is it a code key?
    for prefix in PREFIXES:
        if identifier == prefix[CODE_KEY]:
            return prefix
        
    raise KeyError("No such prefix %s" % str(identifier))


def startColour(status, fgcolour=None, bgcolour=None, prefix=None, wrap=True):
    colourCode = ""
    
    if prefix:
        pre = _getPrefixObj(prefix)
        colourCode += unicode(pre[VAL_KEY])
        
    if fgcolour:
        if colourCode:
            colourCode += ";"
        fgcol = _getColourObj(fgcolour)
        colourCode += unicode(fgcol[VAL_KEY]+FG_OFFSET)

    if bgcolour:
        if colourCode:
            colourCode += ";"
        bgcol = _getColourObj(bgcolour)
        colourCode += unicode(bgcol[VAL_KEY]+BG_OFFSET)

    return _encode(colourCode, wrap=wrap)


def stopColour(status, wrap=True):
    return _encode(RESET_KEY, wrap=wrap)


def colour(status, literal, fgcolour=None, bgcolour=None, prefix=None):
    return startColour(status, fgcolour=fgcolour, bgcolour=bgcolour, prefix=prefix) + \
            literal + \
            stopColour(status)

def _colourFuncFactory(colour):
    def fgfunc(status, literal, prefix=None):
        return startColour(status, fgcolour=colour, prefix=prefix) + literal + stopColour(status)
    def bgfunc(status, literal, prefix=None):
        return startColour(status, bgcolour=colour, prefix=prefix) + literal + stopColour(status)
    return fgfunc, bgfunc


def _populateFunctions(module):
    for colour in COLOURS:
        colourName = colour[NAME_KEY]
        fgfunc, bgfunc = _colourFuncFactory(colourName)
        setattr(module, colourName, fgfunc)
        setattr(module, colourName+"bg", bgfunc)
        

# Populate the functions in this module
_populateFunctions(sys.modules[__name__])
