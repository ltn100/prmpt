#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from test import prmpt
from test import UnitTestWrapper


class ColourTests(UnitTestWrapper):

    def test_getColourCode4Bit(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual(c.RED[c.VAL_KEY], c._getColourCode(c.RED))
        self.assertEqual(c.BLACK[c.VAL_KEY], c._getColourCode("black"))
        self.assertEqual(c.MAGENTA[c.VAL_KEY], c._getColourCode("m"))
        for colour in c.COLOURS:
            self.assertEqual(colour[c.VAL_KEY], c._getColourCode(colour))
            self.assertEqual(colour[c.VAL_KEY], c._getColourCode(colour[c.NAME_KEY]))
            self.assertEqual(colour[c.VAL_KEY], c._getColourCode(colour[c.CODE_KEY]))
        self.assertRaises(ValueError, c._getColourCode, "burple")
        self.assertRaises(ValueError, c._getColourCode, "")

    def test_getColourCodeBg4Bit(self):
        c = prmpt.colours.Colours(None)
        for colour in c.COLOURS:
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._getColourCode(colour, c.BACKGROUND))
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._getColourCode(colour[c.NAME_KEY], c.BACKGROUND))
            self.assertEqual(int(colour[c.VAL_KEY])+c.BG_OFFSET,
                             c._getColourCode(colour[c.CODE_KEY], c.BACKGROUND))
        self.assertRaises(ValueError, c._getColourCode, "burple")

    def test_getColourCode8Bit(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual("38;5;145", c._getColourCode("145"))
        self.assertEqual("38;5;0", c._getColourCode("0"))
        self.assertEqual("38;5;255", c._getColourCode("255"))
        self.assertRaises(ValueError, c._getColourCode, "256")
        self.assertRaises(ValueError, c._getColourCode, "0x456")
        self.assertEqual("38;5;16", c._getColourCode("#000"))
        self.assertEqual("38;5;196", c._getColourCode("#f00"))
        self.assertEqual("38;5;46", c._getColourCode("#0f0"))
        self.assertEqual("38;5;21", c._getColourCode("#00f"))
        self.assertRaises(ValueError, c._getColourCode, "#bat")
        self.assertEqual("38;5;231", c._getColourCode("#gff"))
        self.assertEqual("38;5;16", c._getColourCode("#g00"))
        self.assertEqual("38;5;232", c._getColourCode("#g05"))
        self.assertEqual("38;5;239", c._getColourCode("#g4e"))
        self.assertEqual("38;5;255", c._getColourCode("#gee"))

    def test_getColourCodeBg8Bit(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual("48;5;145", c._getColourCode("145", c.BACKGROUND))

    def test_getColourCode24Bit(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual("38;2;0;0;0", c._getColourCode("#000000"))
        self.assertEqual("38;2;1;2;3", c._getColourCode("#010203"))
        self.assertEqual("38;2;255;255;255", c._getColourCode("#ffffff"))
        self.assertEqual("38;2;0;0;0", c._getColourCode("0,0,0"))
        self.assertEqual("38;2;1;2;3", c._getColourCode("1,2,3"))
        self.assertEqual("38;2;255;255;255", c._getColourCode("255,255,255"))
        self.assertRaises(ValueError, c._getColourCode, "0,0")

    def test_getColourCodeBg24Bit(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual("48;2;1;2;3", c._getColourCode("#010203", c.BACKGROUND))
        self.assertEqual("48;2;1;2;3", c._getColourCode("1,2,3", c.BACKGROUND))

    def test_getStyleCode(self):
        c = prmpt.colours.Colours(None)
        self.assertIs(c._getStyleCode(c.NORMAL), c.NORMAL[c.VAL_KEY])
        self.assertIs(c._getStyleCode("italic"), c.ITALIC[c.VAL_KEY])
        self.assertIs(c._getStyleCode("b"), c.BOLD[c.VAL_KEY])
        for style in c.STYLES:
            self.assertEqual(c._getStyleCode(style), style[c.VAL_KEY])
            self.assertEqual(c._getStyleCode(style[c.NAME_KEY]), style[c.VAL_KEY])
            self.assertEqual(c._getStyleCode(style[c.CODE_KEY]), style[c.VAL_KEY])
        self.assertRaises(KeyError, c._getStyleCode, "upsidedown")

    def test_stopColour(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual(c.stopColour(), "\001\033[0m\002")
        self.assertEqual(c.stopColour(False), "\033[0m")

    def test_startColour(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual(c.startColour("green"), "\001\033[32m\002")
        self.assertEqual(c.startColour("green", _wrap=False), "\033[32m")
        self.assertEqual(c.startColour("red", style="b"), "\001\033[1;31m\002")
        self.assertEqual(c.startColour("1"), "\001\033[38;5;1m\002")
        self.assertEqual(c.startColour(fgcolour="1", bgcolour="2"), "\001\033[38;5;1;48;5;2m\002")

    def test_dynamicColourWrappers(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual(c.green("I'm green"), "\001\033[32m\002I'm green\001\033[0m\002")
        self.assertEqual(c.green("I'm green and bold", "bold"), "\001\033[1;32m\002I'm green and bold\001\033[0m\002")


class ColourFunctionTests(UnitTestWrapper):
    def test_colourLiteral(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.colours)
        self.assertEqual("\001\033[32m\002I'm green\001\033[0m\002",  c._call("green", "I'm green"))
        self.assertEqual("\001\033[31m\002I'm red\001\033[0m\002",    c._call("red", "I'm red"))


class PaletteTests(UnitTestWrapper):
    def test_defaultPalette(self):
        c = prmpt.colours.Colours(None)
        self.assertEqual(c.startColour("info1"), "\001\033[32m\002")
        self.assertEqual(c.startColour("info2"), "\001\033[94m\002")
        self.assertEqual(c.startColour("warning"), "\001\033[33m\002")

    def test_editPalette(self):
        c = prmpt.colours.Colours(None)
        c._setPalette("info1", c.RED)
        self.assertEqual(c.startColour("info1"), "\001\033[31m\002")
        c._setPalette("info1", "123")
        self.assertEqual(c.startColour("info1"), "\001\033[38;5;123m\002")
        c._setPalette("mypal", c.GREEN)
        self.assertEqual(c.startColour("mypal"), "\001\033[32m\002")
