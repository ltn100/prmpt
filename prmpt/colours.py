#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str

# Import external modules
import re
import types
import os

from prmpt import functionBase


class Colours(functionBase.PrmptFunctions):
    NAME_KEY = 0
    CODE_KEY = 1
    VAL_KEY = 2

    FOREGROUND = 1
    BACKGROUND = 2

    # 4-bit colour names
    DEFAULT = {NAME_KEY:    "default",      CODE_KEY: "d",     VAL_KEY: 39}
    BLACK = {NAME_KEY:      "black",        CODE_KEY: "k",     VAL_KEY: 30}
    RED = {NAME_KEY:        "red",          CODE_KEY: "r",     VAL_KEY: 31}
    GREEN = {NAME_KEY:      "green",        CODE_KEY: "g",     VAL_KEY: 32}
    YELLOW = {NAME_KEY:     "yellow",       CODE_KEY: "y",     VAL_KEY: 33}
    BLUE = {NAME_KEY:       "blue",         CODE_KEY: "b",     VAL_KEY: 34}
    MAGENTA = {NAME_KEY:    "magenta",      CODE_KEY: "m",     VAL_KEY: 35}
    CYAN = {NAME_KEY:       "cyan",         CODE_KEY: "c",     VAL_KEY: 36}
    LGREY = {NAME_KEY:      "lightgrey",    CODE_KEY: "lg",    VAL_KEY: 37}
    DGREY = {NAME_KEY:      "darkgrey",     CODE_KEY: "dg",    VAL_KEY: 90}
    LRED = {NAME_KEY:       "lightred",     CODE_KEY: "lr",    VAL_KEY: 91}
    LGREEN = {NAME_KEY:     "lightgreen",   CODE_KEY: "lgn",   VAL_KEY: 92}
    LYELLOW = {NAME_KEY:    "lightyellow",  CODE_KEY: "ly",    VAL_KEY: 93}
    LBLUE = {NAME_KEY:      "lightblue",    CODE_KEY: "lb",    VAL_KEY: 94}
    LMAGENTA = {NAME_KEY:   "lightmagenta", CODE_KEY: "lm",    VAL_KEY: 95}
    LCYAN = {NAME_KEY:      "lightcyan",    CODE_KEY: "lc",    VAL_KEY: 96}
    WHITE = {NAME_KEY:      "white",        CODE_KEY: "w",     VAL_KEY: 97}
    COLOURS = [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, LGREY,
               DGREY, LRED, LGREEN, LYELLOW, LBLUE, LMAGENTA, LCYAN, WHITE,
               DEFAULT]

    # 4-bit colour background offset
    BG_OFFSET = 10

    # Styles
    NORMAL = {NAME_KEY:     "normal",     CODE_KEY: "n",     VAL_KEY: 0}
    BOLD = {NAME_KEY:       "bold",       CODE_KEY: "b",     VAL_KEY: 1}
    DIM = {NAME_KEY:        "dim",        CODE_KEY: "d",     VAL_KEY: 2}
    ITALIC = {NAME_KEY:     "italic",     CODE_KEY: "i",     VAL_KEY: 3}
    UNDERLINE = {NAME_KEY:  "underline",  CODE_KEY: "u",     VAL_KEY: 4}
    BLINK = {NAME_KEY:      "blink",      CODE_KEY: "bl",    VAL_KEY: 5}
    INVERTED = {NAME_KEY:   "inverted",   CODE_KEY: "in",    VAL_KEY: 7}

    STYLES = [NORMAL, BOLD, DIM, ITALIC, UNDERLINE, BLINK, INVERTED]

    RESET_KEY = 0
    NOCOUNT_START_BASH = "\001"
    NOCOUNT_END_BASH = "\002"
    NOCOUNT_START_ZSH = "%{"
    NOCOUNT_END_ZSH = "%}"
    ESCAPE_CHAR = "\033["
    END_CODE = "m"

    if os.environ.get('SHELL', 'sh').split(os.sep)[-1] == "zsh":
        NOCOUNT_START = NOCOUNT_START_ZSH
        NOCOUNT_END = NOCOUNT_END_ZSH
    else:
        NOCOUNT_START = NOCOUNT_START_BASH
        NOCOUNT_END = NOCOUNT_END_BASH

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

        s = self.ESCAPE_CHAR + str(code) + self.END_CODE
        if wrap:
            s = self.NOCOUNT_START + s + self.NOCOUNT_END
        return s

    FG_KEY = 3
    BG_KEY = 4
    STYLE_KEY = 5

    DEFAULT = {NAME_KEY:    'default', FG_KEY: LGREY, BG_KEY: None,  STYLE_KEY: None}
    DIM1 = {NAME_KEY:       'dim1',    FG_KEY: LGREY, BG_KEY: None,  STYLE_KEY: DIM}
    DIM2 = {NAME_KEY:       'dim2',    FG_KEY: DGREY, BG_KEY: None,  STYLE_KEY: BOLD}
    DIM3 = {NAME_KEY:       'dim3',    FG_KEY: DGREY, BG_KEY: None,  STYLE_KEY: None}
    BRIGHT = {NAME_KEY:     'bright',  FG_KEY: WHITE, BG_KEY: None,  STYLE_KEY: None}
    ERROR = {NAME_KEY:      'error',   FG_KEY: LRED,  BG_KEY: None,  STYLE_KEY: None}
    WARNING = {NAME_KEY:    'warning', FG_KEY: YELLOW, BG_KEY: None,  STYLE_KEY: None}
    INFO1 = {NAME_KEY:      'info1',   FG_KEY: GREEN, BG_KEY: None,  STYLE_KEY: None}
    INFO2 = {NAME_KEY:      'info2',   FG_KEY: LBLUE, BG_KEY: None,  STYLE_KEY: None}
    INFO3 = {NAME_KEY:      'info3',   FG_KEY: LMAGENTA, BG_KEY: None, STYLE_KEY: None}
    PALETTE = [DIM1, DIM2, DIM3, BRIGHT, ERROR, WARNING, INFO1, INFO2, INFO3]

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
            pal = {self.NAME_KEY: str(identifier),  self.FG_KEY: None, self.BG_KEY: None,  self.STYLE_KEY: None}
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
                style = str(self._getStyleCode(pal[self.STYLE_KEY]))
                fg = str(self._getColourCode(pal[self.FG_KEY], self.FOREGROUND))
                bg = str(self._getColourCode(pal[self.BG_KEY], self.BACKGROUND))
                return ";".join([x for x in [style, fg, bg] if x])

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
            if not re.match("^#[0-9a-fA-Fg][0-9a-fA-F][0-9a-fA-F]$", identifier):
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
                nearest_segments = [0, 0, 0]  # R,G,B

                for i in range(3):
                    hex_val = (int(identifier[i+1], 16)*16)+7
                    for idx, v in enumerate(self.NEAREST_8BIT_CODE):
                        if hex_val <= v:
                            nearest_segments[i] = idx
                            break

                identifier = \
                    nearest_segments[0]*36 + \
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
            if not re.match("^#[0-9a-fA-F]{6}$", identifier):
                raise ValueError

            r = int(identifier[1:3], 16)
            g = int(identifier[3:5], 16)
            b = int(identifier[5:7], 16)
            return "%s%d;%d;%d" % (style, r, g, b)

        # Assume the format "r,g,b"
        try:
            (r, g, b) = identifier.split(',')
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
            colourCode = self._get4bitColourCode(identifier, area)
            return colourCode
        except ValueError:
            pass

        try:
            colourCode = self._get8bitColourCode(identifier, area)
            return colourCode
        except ValueError:
            pass

        try:
            colourCode = self._get24bitColourCode(identifier, area)
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

    @staticmethod
    def _colourFuncFactory(clr):
        def fgfunc(slf, literal, style=None):
            return slf.startColour(fgcolour=clr, style=style) + \
                    literal + \
                    slf.stopColour()

        def bgfunc(slf, literal, style=None):
            return slf.startColour(bgcolour=clr, style=style) + \
                    literal + \
                    slf.stopColour()

        fgfunc.__doc__ = """
        Set {} foreground colour for ``literal``.

        :param style: The character style.
        """.format(clr)

        bgfunc.__doc__ = """
        Set {} background colour for ``literal``.

        :param style: The character style.
        """.format(clr)

        return fgfunc, bgfunc

    @staticmethod
    def _styleFuncFactory(style):
        def func(slf, literal):
            return slf.startColour(style=style) + \
                    literal + \
                    slf.stopColour()

        func.__doc__ = """
        Set the style to {} for ``literal``.
        """.format(style)

        return func

    @staticmethod
    def _paletteFuncFactory(pal):
        def func(slf, literal):
            return slf.startColour(fgcolour=pal) + \
                    literal + \
                    slf.stopColour()

        func.__doc__ = """
        Set the pallet colour to {} for ``literal``.
        """.format(pal)

        return func

    @staticmethod
    def _populateFunctions():
        """
        This will define functions for all 4-bit colours.
        The function definitions are of the form:
            red(literal, style)     # fg red
            redbg(literal, style)   # bg red
        Also styles are defined, e.g.:
            bold(literal)

        """
        for c in Colours.COLOURS:
            colourName = c[Colours.NAME_KEY]
            fgfunc, bgfunc = Colours._colourFuncFactory(colourName)
            setattr(Colours, colourName, fgfunc)
            setattr(Colours, colourName+"bg", bgfunc)
        for s in Colours.STYLES:
            styleName = s[Colours.NAME_KEY]
            func = Colours._styleFuncFactory(styleName)
            setattr(Colours, styleName, func)
        for p in Colours.PALETTE:
            paletteName = p[Colours.NAME_KEY]
            func = Colours._paletteFuncFactory(paletteName)
            setattr(Colours, paletteName, func)

    # ------------------------
    # Public methods
    # ------------------------
    def startColour(self, fgcolour=None, bgcolour=None, style=None, _wrap=True):
        """
        Start a colour block.

        :param fgcolour: The foreground colour.
        :param bgcolour: The background colour.
        :param style: The character style.
        """
        colourCode = ""

        if style:
            colourCode += str(self._getStyleCode(style))

        if fgcolour:
            if colourCode:
                colourCode += ";"
            colourCode += str(self._getColourCode(fgcolour, self.FOREGROUND))

        if bgcolour:
            if colourCode:
                colourCode += ";"
            colourCode += str(self._getColourCode(bgcolour, self.BACKGROUND))

        return self._encode(colourCode, wrap=_wrap)

    def stopColour(self, _wrap=True):
        """
        Stop a colour block.

        :param wrap: Wrap the code in additional characters
                to signify non-printing characters are
                contained
        """
        return self._encode(self.RESET_KEY, wrap=_wrap)

    def colour(self, literal, fgcolour=None, bgcolour=None, style=None, _wrap=True):
        """
        Wrap the string ``literal`` in a colour block. The colour is stopped when ``literal`` ends.

        :param fgcolour: The foreground colour.
        :param bgcolour: The background colour.
        :param style: The character style.
        """
        return self.startColour(fgcolour=fgcolour, bgcolour=bgcolour, style=style, _wrap=_wrap) + \
            literal + \
            self.stopColour(_wrap=_wrap)


# Populate the functions in this module
Colours._populateFunctions()
