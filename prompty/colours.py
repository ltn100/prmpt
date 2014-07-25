#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys

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
NOCOUNT_START   = u"\001"
NOCOUNT_END     = u"\002"
ESCAPE_CHAR     = u"\033["
END_CODE        = u"m"


def _encode(code, wrap=True):
    s = ESCAPE_CHAR+\
            unicode(code)+\
            END_CODE
    if wrap:
        s = NOCOUNT_START+\
            s+\
            NOCOUNT_END
    return s


def _getColourObj(identifier):
    # Is it a colour dict?
    if identifier in COLOURS:
        return identifier
    
    # Is it a name key?
    for colour in COLOURS:
        if identifier == colour[NAME_KEY]:
            return colour

    # Is it a code key?
    for colour in COLOURS:
        if identifier == colour[CODE_KEY]:
            return colour
        
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


def startColour(status, colour, prefix=FG_PREFIX, wrap=True):
    col = _getColourObj(colour)
    pre = _getPrefixObj(prefix)
    return _encode("%s%s" % (unicode(pre[VAL_KEY]), unicode(col[VAL_KEY])), wrap=wrap)


def stopColour(status, wrap=True):
    return _encode(RESET_KEY, wrap=wrap)


def _colourFuncFactory(colour):
    def func(status, literal, prefix=FG_PREFIX):
        return startColour(status, colour, prefix) + literal + stopColour(status)
    return func


def _populateFunctions(module):
    for colour in COLOURS:
        colourName = colour[NAME_KEY]
        setattr(module, colourName, _colourFuncFactory(colourName))
        

# Populate the functions in this module
_populateFunctions(sys.modules[__name__])
