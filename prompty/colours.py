#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import re
import types

import functionBase

class Colours(functionBase.PromptyFunctions):

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

    def __init__(self, container):
        self._populateFunctions()
        super(Colours, self).__init__(container)


    def _encode(self, code, wrap=True):
        """
        Add the bash escape codes for colours
        i.e.: \\e[CODEm

        :param wrap: Wrap the code in additional characters
                     to signify non-printing characters are
                     contained
        """
        if code == "":
            return ""

        s = self.ESCAPE_CHAR+\
                unicode(code)+\
                self.END_CODE
        if wrap:
            s = self.NOCOUNT_START+\
                s+\
                self.NOCOUNT_END
        return s

    FG_KEY      = 3
    BG_KEY      = 4
    STYLE_KEY   = 5


    PALC1 = {NAME_KEY : 'pal_c1',  FG_KEY : WHITE, BG_KEY : None,  STYLE_KEY : None}
    PALC2 = {NAME_KEY : 'pal_c2',  FG_KEY : LGREY, BG_KEY : None,  STYLE_KEY : None}
    PALC3 = {NAME_KEY : 'pal_c3',  FG_KEY : LGREY, BG_KEY : None,  STYLE_KEY : DIM}
    PALC4 = {NAME_KEY : 'pal_c4',  FG_KEY : DGREY, BG_KEY : None,  STYLE_KEY : BOLD}
    PALC5 = {NAME_KEY : 'pal_c5',  FG_KEY : DGREY, BG_KEY : None,  STYLE_KEY : None}
    PALA1 = {NAME_KEY : 'pal_a1',  FG_KEY : LRED,  BG_KEY : None,  STYLE_KEY : None}
    PALA2 = {NAME_KEY : 'pal_a2',  FG_KEY : YELLOW,BG_KEY : None,  STYLE_KEY : None}
    PALA3 = {NAME_KEY : 'pal_a3',  FG_KEY : GREEN, BG_KEY : None,  STYLE_KEY : None}
    PALA4 = {NAME_KEY : 'pal_a4',  FG_KEY : LBLUE, BG_KEY : None,  STYLE_KEY : None}
    PALA5 = {NAME_KEY : 'pal_a5',  FG_KEY : LMAGENTA,BG_KEY : None, STYLE_KEY : None}
    PALETTE = [PALC1,PALC2,PALC3,PALC4,PALC5,PALA1,PALA2,PALA3,PALA4,PALA5]


    def _setPalette(self, identifier, fgcolour=None, bgcolour=None, style=None):
        if identifier is None:
            return

        found = False
        for pal in self.PALETTE:
            if identifier == pal[self.NAME_KEY]:
                found = True
                break

        if not found:
            # Create a new palette member
            pal = {self.NAME_KEY : str(identifier),  self.FG_KEY : None, self.BG_KEY : None,  self.STYLE_KEY : None}
            self.PALETTE.append(pal)

        # Update the palette
        if fgcolour:
            pal[self.FG_KEY] = fgcolour
        if bgcolour:
            pal[self.BG_KEY] = bgcolour
        if style:
            pal[self.STYLE_KEY] = style



    def _getPaletteColourCode(self, identifier):
        """
        Palette colour codes can be any of the following:
            pal1, pal2, etc.
        """
        if identifier is None:
            return ""

        for pal in self.PALETTE:
            if identifier == pal[self.NAME_KEY]:
                style   = unicode(self._getStyleCode(pal[self.STYLE_KEY]))
                fg      = unicode(self._getColourCode(pal[self.FG_KEY], self.FOREGROUND))
                bg      = unicode(self._getColourCode(pal[self.BG_KEY], self.BACKGROUND))
                return ";".join([x for x in [style,fg,bg] if x])

        raise ValueError


    def _get4bitColourCode(self, identifier, area=FOREGROUND):
        """
        4-bit colour codes can be any of the following:
            r, red, lr, lightred, etc.
        """
        if identifier is None:
            return ""

        if area == self.FOREGROUND:
            offset = 0
        else:
            offset = self.BG_OFFSET

        if isinstance(identifier, dict):
            # Is it a colour dict?
            if identifier in self.COLOURS:
                return identifier[self.VAL_KEY]+offset
        else:
            # Assume identifier is a sting
            if len(identifier) == 0:
                raise ValueError("No such colour %s" % str(identifier))

            # Is it a name key?
            for c in self.COLOURS:
                if identifier == c[self.NAME_KEY]:
                    return c[self.VAL_KEY]+offset

            # Is it a code key?
            for c in self.COLOURS:
                if identifier == c[self.CODE_KEY]:
                    return c[self.VAL_KEY]+offset

        raise ValueError

    NEAREST_8BIT_CODE = [0x30, 0x73, 0x9b, 0xc3, 0x3b, 0xff]
    NEAREST_8BIT_GREY_CODE = [0x04, 0x0d, 0x17, 0x21, 0x2b, 0x35, 0x3f, 0x49, 0x53,
                              0x5c, 0x63, 0x6e, 0x7b, 0x85, 0x8f, 0x99, 0xa3, 0xad,
                              0xb7, 0xc1, 0xcb, 0xd5, 0xdf, 0xe9, 0xf7, 0xff]



    def _get8bitColourCode(self, identifier, area=FOREGROUND):
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

        if area == self.FOREGROUND:
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
                for idx, v in enumerate(self.NEAREST_8BIT_GREY_CODE):
                    if hex_val <= v:
                        nearest_segment = idx
                        break

                if nearest_segment == 0:
                    identifier = 16
                elif nearest_segment == len(self.NEAREST_8BIT_GREY_CODE)-1:
                    identifier = 231
                else:
                    identifier = nearest_segment+231
                return "%s%d" % (style, identifier)
            else:
                nearest_segments = [0,0,0] # R,G,B

                for i in xrange(3):
                    hex_val = (int(identifier[i+1], 16)*16)+7
                    for idx, v in enumerate(self.NEAREST_8BIT_CODE):
                        if hex_val <= v:
                            nearest_segments[i] = idx
                            break

                identifier =    nearest_segments[0]*36 + \
                                nearest_segments[1]*6 + \
                                nearest_segments[2] + 16
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

    def _get24bitColourCode(self, identifier, area=FOREGROUND):
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

        if area == self.FOREGROUND:
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


    def _getColourCode(self, identifier, area=FOREGROUND):
        try:
            colourCode = self._getPaletteColourCode(identifier)
            return colourCode
        except ValueError:
            pass

        try:
            colourCode = self._get4bitColourCode(identifier,area)
            return colourCode
        except ValueError:
            pass

        try:
            colourCode = self._get8bitColourCode(identifier,area)
            return colourCode
        except ValueError:
            pass

        try:
            colourCode = self._get24bitColourCode(identifier,area)
            return colourCode
        except ValueError:
            pass

        raise ValueError("No such colour %s" % str(identifier))


    def _getStyleCode(self, identifier):
        if identifier is None:
            return ""

        # Is it a style dict?
        if identifier in self.STYLES:
            return identifier[self.VAL_KEY]

        # Is it a name key?
        for style in self.STYLES:
            if identifier == style[self.NAME_KEY]:
                return style[self.VAL_KEY]

        # Is it a code key?
        for style in self.STYLES:
            if identifier == style[self.CODE_KEY]:
                return style[self.VAL_KEY]

        raise KeyError("No such style %s" % str(identifier))


    def startColour(self, fgcolour=None, bgcolour=None, style=None, wrap=True):
        colourCode = ""

        if style:
            colourCode += unicode(self._getStyleCode(style))

        if fgcolour:
            if colourCode:
                colourCode += ";"
            colourCode += unicode(self._getColourCode(fgcolour, self.FOREGROUND))

        if bgcolour:
            if colourCode:
                colourCode += ";"
            colourCode += unicode(self._getColourCode(bgcolour, self.BACKGROUND))

        return self._encode(colourCode, wrap=wrap)


    def stopColour(self, wrap=True):
        return self._encode(self.RESET_KEY, wrap=wrap)


    def colour(self, literal, fgcolour=None, bgcolour=None, style=None, wrap=True):
        return self.startColour(fgcolour=fgcolour, bgcolour=bgcolour, style=style, wrap=wrap) + \
                literal + \
                self.stopColour(wrap=wrap)


    def _colourFuncFactory(self, clr):
        def fgfunc(slf, literal, style=None):
            return  self.startColour(fgcolour=clr, style=style) + \
                    literal + \
                    self.stopColour()
        def bgfunc(slf, literal, style=None):
            return  self.startColour(bgcolour=clr, style=style) + \
                    literal + \
                    self.stopColour()
        return fgfunc, bgfunc


    def _styleFuncFactory(self, style):
        def func(slf, literal):
            return  self.startColour(style=style) + \
                    literal + \
                    self.stopColour()
        return func

    def _paletteFuncFactory(self, pal):
        def func(slf, literal):
            return  self.startColour(fgcolour=pal) + \
                    literal + \
                    self.stopColour()
        return func

    def _populateFunctions(self):
        """
        This will define functions for all 4-bit colours.
        The function definitions are of the form:
            red(literal, style)     # fg red
            redbg(literal, style)   # bg red
        Also styles are defined, e.g.:
            bold(literal)

        """
        for c in self.COLOURS:
            colourName = c[self.NAME_KEY]
            fgfunc, bgfunc = self._colourFuncFactory(colourName)
            setattr(self, colourName, types.MethodType(fgfunc, self))
            setattr(self, colourName+"bg", types.MethodType(bgfunc, self))
        for s in self.STYLES:
            styleName = s[self.NAME_KEY]
            func = self._styleFuncFactory(styleName)
            setattr(self, styleName, types.MethodType(func, self))
        for p in self.PALETTE:
            paletteName = p[self.NAME_KEY]
            func = self._paletteFuncFactory(paletteName)
            setattr(self, paletteName, types.MethodType(func, self))


# Populate the functions in this module
#_populateFunctions(sys.modules[__name__])
