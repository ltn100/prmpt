#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import re

NAME_KEY = 0
CODE_KEY = 1
VAL_KEY  = 2


FOREGROUND = 1
BACKGROUND = 2


# 4-bit colour names
DEFAULT = {NAME_KEY : "default",    CODE_KEY : "d",     VAL_KEY : 39}
BLACK   = {NAME_KEY : "black",      CODE_KEY : "k",     VAL_KEY : 30}
RED     = {NAME_KEY : "red",        CODE_KEY : "r",     VAL_KEY : 31}
GREEN   = {NAME_KEY : "green",      CODE_KEY : "g",     VAL_KEY : 32}
YELLOW  = {NAME_KEY : "yellow",     CODE_KEY : "y",     VAL_KEY : 33}
BLUE    = {NAME_KEY : "blue",       CODE_KEY : "b",     VAL_KEY : 34}
MAGENTA = {NAME_KEY : "magenta",    CODE_KEY : "m",     VAL_KEY : 35}
CYAN    = {NAME_KEY : "cyan",       CODE_KEY : "c",     VAL_KEY : 36}
LGREY   = {NAME_KEY : "lightgrey",  CODE_KEY : "lg",    VAL_KEY : 37}
DGREY   = {NAME_KEY : "darkgrey",   CODE_KEY : "dg",    VAL_KEY : 90}
LRED    = {NAME_KEY : "lightred",   CODE_KEY : "lr",    VAL_KEY : 91}
LGREEN  = {NAME_KEY : "lightgreen", CODE_KEY : "lgn",   VAL_KEY : 92}
LYELLOW = {NAME_KEY : "lightyellow",CODE_KEY : "ly",    VAL_KEY : 93}
LBLUE   = {NAME_KEY : "lightblue",  CODE_KEY : "lb",    VAL_KEY : 94}
LMAGENTA= {NAME_KEY : "lightmagenta",CODE_KEY :"lm",    VAL_KEY : 95}
LCYAN   = {NAME_KEY : "lightcyan",  CODE_KEY : "lc",    VAL_KEY : 96}
WHITE   = {NAME_KEY : "white",      CODE_KEY : "w",     VAL_KEY : 97}
COLOURS = [BLACK,RED,GREEN,YELLOW,BLUE,MAGENTA,CYAN,LGREY,
           DGREY,LRED,LGREEN,LYELLOW,LBLUE,LMAGENTA,LCYAN,WHITE]

# 4-bit colour background offset
BG_OFFSET = 10



# Styles
NORMAL      = {NAME_KEY : "normal",     CODE_KEY : "n",     VAL_KEY : 0}
BOLD        = {NAME_KEY : "bold",       CODE_KEY : "b",     VAL_KEY : 1}
DIM         = {NAME_KEY : "dim",        CODE_KEY : "d",     VAL_KEY : 2}
ITALIC      = {NAME_KEY : "italic",     CODE_KEY : "i",     VAL_KEY : 3}
UNDERLINE   = {NAME_KEY : "underline",  CODE_KEY : "u",     VAL_KEY : 4}
BLINK       = {NAME_KEY : "blink",      CODE_KEY : "bl",    VAL_KEY : 5}
INVERTED    = {NAME_KEY : "inverted",   CODE_KEY : "in",    VAL_KEY : 7}

STYLES = [NORMAL,BOLD,DIM,ITALIC,UNDERLINE,BLINK,INVERTED]

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
    if code == "":
        return ""
    
    s = ESCAPE_CHAR+\
            unicode(code)+\
            END_CODE
    if wrap:
        s = NOCOUNT_START+\
            s+\
            NOCOUNT_END
    return s

FG_KEY      = 3
BG_KEY      = 4
STYLE_KEY   = 5

PAL1 = {NAME_KEY : 'pal1',  FG_KEY : None,  BG_KEY : None,  STYLE_KEY : None}
PAL2 = {NAME_KEY : 'pal2',  FG_KEY : GREEN, BG_KEY : None,  STYLE_KEY : None}
PAL3 = {NAME_KEY : 'pal3',  FG_KEY : LBLUE, BG_KEY : None,  STYLE_KEY : BOLD}
PALETTE = [PAL1,PAL2,PAL3]


def _getPaletteColourCode(identifier, area=None):
    """
    Palette colour codes can be any of the following:
        pal1, pal2, etc.
    """
    if identifier is None:
        return ""

    for pal in PALETTE:
        if identifier == pal[NAME_KEY]:
            style   = unicode(_getStyleCode(pal[STYLE_KEY]))
            fg      = unicode(_getColourCode(pal[FG_KEY], FOREGROUND))
            bg      = unicode(_getColourCode(pal[BG_KEY], BACKGROUND))
            return ";".join(filter(None, [style,fg,bg]))
    
    raise ValueError
    

def _get4bitColourCode(identifier, area=FOREGROUND):
    """
    4-bit colour codes can be any of the following:
        r, red, lr, lightred, etc.
    """
    if identifier is None:
        return ""

    if area == FOREGROUND:
        offset = 0
    else:
        offset = BG_OFFSET
        
    if isinstance(identifier, dict):
        # Is it a colour dict?
        if identifier in COLOURS:
            return identifier[VAL_KEY]+offset
    else:
        # Assume identifier is a sting
        if len(identifier) == 0:
            raise ValueError("No such colour %s" % str(identifier))
        
        # Is it a name key?
        for colour in COLOURS:
            if identifier == colour[NAME_KEY]:
                return colour[VAL_KEY]+offset
            
        # Is it a code key?
        for colour in COLOURS:
            if identifier == colour[CODE_KEY]:
                return colour[VAL_KEY]+offset
    
    raise ValueError

NEAREST_8BIT_CODE = [0x30, 0x73, 0x9b, 0xc3, 0x3b, 0xff]
NEAREST_8BIT_GREY_CODE = [0x04, 0x0d, 0x17, 0x21, 0x2b, 0x35, 0x3f, 0x49,
                          0x53, 0x5c, 0x63, 0x6e, 0x7b, 0x85, 0x8f, 0x99, 
                          0xa3, 0xad, 0xb7, 0xc1, 0xcb, 0xd5, 0xdf, 0xe9, 0xf7, 0xff]



def _get8bitColourCode(identifier, area=FOREGROUND):
    """
    8-bit colour codes can be any of the following:
        0, 5, 126, 255, #0f0, #fff, #a3e, etc.
    """
    if identifier is None:
        return ""
    
    # Assume identifier is a sting
    identifier = str(identifier)
    if len(identifier) == 0:
        raise ValueError("No such colour %s" % str(identifier))
    
    if area == FOREGROUND:
        style = "38;5;"
    else:
        style = "48;5;"
    
    # Check lead char
    if identifier[0] == "#":
        if not re.match("^#[0-9a-fA-Fg][0-9a-fA-F][0-9a-fA-F]$",identifier):
            raise ValueError
        
        if identifier[1] == 'g':
            # Grey-scale values
            hex_val = int(identifier[2:4], 16)
            nearest_segment = 0
            for idx, v in enumerate(NEAREST_8BIT_GREY_CODE):
                if hex_val <= v:
                    nearest_segment = idx
                    break

            if nearest_segment == 0:
                identifier = 16
            elif nearest_segment == len(NEAREST_8BIT_GREY_CODE)-1:
                identifier = 231
            else:
                identifier = nearest_segment+231
            return "%s%d" % (style, identifier)
        
        else:
            nearest_segments = [0,0,0] # R,G,B
            
            for i in xrange(3):
                hex_val = (int(identifier[i+1], 16)*16)+7
                for idx, v in enumerate(NEAREST_8BIT_CODE):
                    if hex_val <= v:
                        nearest_segments[i] = idx
                        break
    
            identifier = nearest_segments[0]*36 + nearest_segments[1]*6 +nearest_segments[2] + 16
            return "%s%d" % (style, identifier)

    try:
        # Check for valid integer value
        identifier = int(identifier)
        if identifier < 0 or identifier > 255:
            raise ValueError
        return "%s%d" % (style, identifier)
    except ValueError:
        pass
    
    
    raise ValueError

def _get24bitColourCode(identifier, area=FOREGROUND):
    """
    24-bit colour codes can be any of the following:
        #000000, #aaf4d3, 0,255,0, 255,255,255 
        
    24-bit colours are onlt supported by Konsole at the moment:
    https://github.com/robertknight/konsole/blob/master/user-doc/README.moreColors
    """
    if identifier is None:
        return ""
    
    # Assume identifier is a sting
    identifier = str(identifier)
    if len(identifier) == 0:
        raise ValueError("No such colour %s" % str(identifier))
    
    if area == FOREGROUND:
        style = "38;2;"
    else:
        style = "48;2;"
    
    # Check lead char
    if identifier[0] == "#":
        if not re.match("^#[0-9a-fA-F]{6}$",identifier):
            raise ValueError
        
        r = int(identifier[1:3], 16)
        g = int(identifier[3:5], 16)
        b = int(identifier[5:7], 16)
        return "%s%d;%d;%d" % (style, r, g, b)
    
    # Assume the format "r,g,b"
    try:
        (r,g,b) = identifier.split(',')
        return "%s%d;%d;%d" % (style, int(r), int(g), int(b))
    except ValueError:
        pass
    
    raise ValueError



def _getColourCode(identifier, area=FOREGROUND):
    try:
        colourCode = _getPaletteColourCode(identifier,area)
        return colourCode
    except ValueError:
        pass
    
    try:
        colourCode = _get4bitColourCode(identifier,area)
        return colourCode
    except ValueError:
        pass
    
    try:
        colourCode = _get8bitColourCode(identifier,area)
        return colourCode
    except ValueError:
        pass

    try:
        colourCode = _get24bitColourCode(identifier,area)
        return colourCode
    except ValueError:
        pass
    
    raise ValueError("No such colour %s" % str(identifier))

def _getStyleCode(identifier):
    if identifier is None:
        return ""
    
    # Is it a style dict?
    if identifier in STYLES:
        return identifier[VAL_KEY]
    
    # Is it a name key?
    for style in STYLES:
        if identifier == style[NAME_KEY]:
            return style[VAL_KEY]

    # Is it a code key?
    for style in STYLES:
        if identifier == style[CODE_KEY]:
            return style[VAL_KEY]
        
    raise KeyError("No such style %s" % str(identifier))


def startColour(status, fgcolour=None, bgcolour=None, style=None, wrap=True):
    colourCode = ""
    
    if style:
        colourCode += unicode(_getStyleCode(style))
        
    if fgcolour:
        if colourCode:
            colourCode += ";"
        colourCode += unicode(_getColourCode(fgcolour, FOREGROUND))

    if bgcolour:
        if colourCode:
            colourCode += ";"
        colourCode += unicode(_getColourCode(bgcolour, BACKGROUND))

    return _encode(colourCode, wrap=wrap)


def stopColour(status, wrap=True):
    return _encode(RESET_KEY, wrap=wrap)


def colour(status, literal, fgcolour=None, bgcolour=None, style=None, wrap=True):
    return startColour(status, fgcolour=fgcolour, bgcolour=bgcolour, style=style, wrap=wrap) + \
            literal + \
            stopColour(status, wrap=wrap)


def _colourFuncFactory(colour):
    def fgfunc(status, literal, style=None):
        return startColour(status, fgcolour=colour, style=style) + literal + stopColour(status)
    def bgfunc(status, literal, style=None):
        return startColour(status, bgcolour=colour, style=style) + literal + stopColour(status)
    return fgfunc, bgfunc

def _styleFuncFactory(style):
    def func(status, literal):
        return startColour(status, style=style) + literal + stopColour(status)
    return func


def _populateFunctions(module):
    """
    This will define functions for all 4-bit colours.
    The function definitions are of the form:
        red(literal, style)     # fg red
        redbg(literal, style)   # bg red
    Also styles are defined, e.g.:
        bold(literal)
        
    """
    for colour in COLOURS:
        colourName = colour[NAME_KEY]
        fgfunc, bgfunc = _colourFuncFactory(colourName)
        setattr(module, colourName, fgfunc)
        setattr(module, colourName+"bg", bgfunc)
    for style in STYLES:
        styleName = style[NAME_KEY]
        func = _styleFuncFactory(styleName)
        setattr(module, styleName, func)


# Populate the functions in this module
_populateFunctions(sys.modules[__name__])
