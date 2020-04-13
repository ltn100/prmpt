#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from test import prompty
from test import UnitTestWrapper


class ColourTests(UnitTestWrapper):

    def test_getColourCode4Bit(self):
        c = prompty.colours.Colours(None)
        self.assertEqual(c.RED[c.VAL_KEY], c._get_colour_code(c.RED))
        self.assertEqual(c.BLACK[c.VAL_KEY], c._get_colour_code("black"))
        self.assertEqual(c.MAGENTA[c.VAL_KEY], c._get_colour_code("m"))
        for colour in c.COLOURS:
            self.assertEqual(colour[c.VAL_KEY], c._get_colour_code(colour))
            self.assertEqual(colour[c.VAL_KEY], c._get_colour_code(colour[c.NAME_KEY]))
            self.assertEqual(colour[c.VAL_KEY], c._get_colour_code(colour[c.CODE_KEY]))
        self.assertRaises(ValueError, c._get_colour_code, "burple")
        self.assertRaises(ValueError, c._get_colour_code, "")

    def test_getColourCodeBg4Bit(self):
        c = prompty.colours.Colours(None)
        for colour in c.COLOURS:
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._get_colour_code(colour, c.BACKGROUND))
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._get_colour_code(colour[c.NAME_KEY], c.BACKGROUND))
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._get_colour_code(colour[c.CODE_KEY], c.BACKGROUND))
        self.assertRaises(ValueError, c._get_colour_code, "burple")

    def test_getColourCode8Bit(self):
        c = prompty.colours.Colours(None)
        self.assertEqual("38;5;145", c._get_colour_code("145"))
        self.assertEqual("38;5;0", c._get_colour_code("0"))
        self.assertEqual("38;5;255", c._get_colour_code("255"))
        self.assertRaises(ValueError, c._get_colour_code, "256")
        self.assertRaises(ValueError, c._get_colour_code, "0x456")
        self.assertEqual("38;5;16", c._get_colour_code("#000"))
        self.assertEqual("38;5;196", c._get_colour_code("#f00"))
        self.assertEqual("38;5;46", c._get_colour_code("#0f0"))
        self.assertEqual("38;5;21", c._get_colour_code("#00f"))
        self.assertRaises(ValueError, c._get_colour_code, "#bat")
        self.assertEqual("38;5;231", c._get_colour_code("#gff"))
        self.assertEqual("38;5;16", c._get_colour_code("#g00"))
        self.assertEqual("38;5;232", c._get_colour_code("#g05"))
        self.assertEqual("38;5;239", c._get_colour_code("#g4e"))
        self.assertEqual("38;5;255", c._get_colour_code("#gee"))

    def test_getColourCodeBg8Bit(self):
        c = prompty.colours.Colours(None)
        self.assertEqual("48;5;145", c._get_colour_code("145", c.BACKGROUND))

    def test_getColourCode24Bit(self):
        c = prompty.colours.Colours(None)
        self.assertEqual("38;2;0;0;0", c._get_colour_code("#000000"))
        self.assertEqual("38;2;1;2;3", c._get_colour_code("#010203"))
        self.assertEqual("38;2;255;255;255", c._get_colour_code("#ffffff"))
        self.assertEqual("38;2;0;0;0", c._get_colour_code("0,0,0"))
        self.assertEqual("38;2;1;2;3", c._get_colour_code("1,2,3"))
        self.assertEqual("38;2;255;255;255", c._get_colour_code("255,255,255"))
        self.assertRaises(ValueError, c._get_colour_code, "0,0")

    def test_getColourCodeBg24Bit(self):
        c = prompty.colours.Colours(None)
        self.assertEqual("48;2;1;2;3", c._get_colour_code("#010203", c.BACKGROUND))
        self.assertEqual("48;2;1;2;3", c._get_colour_code("1,2,3", c.BACKGROUND))

    def test_getStyleCode(self):
        c = prompty.colours.Colours(None)
        self.assertIs(c._get_style_code(c.NORMAL), c.NORMAL[c.VAL_KEY])
        self.assertIs(c._get_style_code("italic"), c.ITALIC[c.VAL_KEY])
        self.assertIs(c._get_style_code("b"), c.BOLD[c.VAL_KEY])
        for style in c.STYLES:
            self.assertEqual(c._get_style_code(style), style[c.VAL_KEY])
            self.assertEqual(c._get_style_code(style[c.NAME_KEY]), style[c.VAL_KEY])
            self.assertEqual(c._get_style_code(style[c.CODE_KEY]), style[c.VAL_KEY])
        self.assertRaises(KeyError, c._get_style_code, "upsidedown")

    def test_stopColour(self):
        c = prompty.colours.Colours(None)
        self.assertEqual(c.stopcolour(), "\001\033[0m\002")
        c.status.wrap = False
        self.assertEqual(c.stopcolour(), "\033[0m")

    def test_startColour(self):
        c = prompty.colours.Colours(None)
        self.assertEqual(c.startcolour("green"), "\001\033[32m\002")
        c.status.wrap = False
        self.assertEqual(c.startcolour("green"), "\033[32m")
        c.status.wrap = True
        self.assertEqual(c.startcolour("red", style="b"), "\001\033[1;31m\002")
        self.assertEqual(c.startcolour("1"), "\001\033[38;5;1m\002")
        self.assertEqual(c.startcolour(fgcolour="1", bgcolour="2"), "\001\033[38;5;1;48;5;2m\002")

    def test_dynamicColourWrappers(self):
        c = prompty.colours.Colours(None)
        self.assertEqual(c.green("I'm green"), "\001\033[32m\002I'm green\001\033[0m\002")
        self.assertEqual(c.green("I'm green and bold", "bold"), "\001\033[1;32m\002I'm green and bold\001\033[0m\002")


class ColourFunctionTests(UnitTestWrapper):
    def test_colourLiteral(self):
        c = prompty.functionContainer.FunctionContainer()
        c.add_functions_from_module(prompty.colours)
        self.assertEqual("\001\033[32m\002I'm green\001\033[0m\002",  c._call("green", "I'm green"))
        self.assertEqual("\001\033[31m\002I'm red\001\033[0m\002",    c._call("red", "I'm red"))


class PaletteTests(UnitTestWrapper):
    def test_defaultPalette(self):
        c = prompty.colours.Colours(None)
        self.assertEqual(c.startcolour("info1"), "\001\033[32m\002")
        self.assertEqual(c.startcolour("info2"), "\001\033[94m\002")
        self.assertEqual(c.startcolour("warning"), "\001\033[33m\002")

    def test_editPalette(self):
        c = prompty.colours.Colours(None)
        c._set_palette("info1", c.RED)
        self.assertEqual(c.startcolour("info1"), "\001\033[31m\002")
        c._set_palette("info1", "123")
        self.assertEqual(c.startcolour("info1"), "\001\033[38;5;123m\002")
        c._set_palette("mypal", c.GREEN)
        self.assertEqual(c.startcolour("mypal"), "\001\033[32m\002")
