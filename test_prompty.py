#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import unittest
from contextlib import contextmanager
from StringIO import StringIO

import prompty


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err



class MainTests(unittest.TestCase):
    def test_help(self):
        argv = ["","-h"]
        with captured_output() as (out, err):
            ret = prompty.main(argv)

        self.assertEqual(out.getvalue(), "")
        self.assertGreater(len(err.getvalue()), 0)
        self.assertEqual(ret, 0)

    def test_bash(self):
        argv = ["","-b"]
        with captured_output() as (out, err):
            ret = prompty.main(argv)

        self.assertTrue(out.getvalue().startswith("export PS1"))
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

class ColourTests(unittest.TestCase):
    def test_getColourObj(self):
        c = prompty.Colour()
        self.assertIs(c._getColourObj(c.RED), c.RED)
        self.assertIs(c._getColourObj("black"), c.BLACK)
        self.assertIs(c._getColourObj("m"), c.MAGENTA)
        for colour in c.COLOURS:
            self.assertIs(c._getColourObj(colour), colour)
            self.assertIs(c._getColourObj(colour[c.NAME_KEY]), colour)
            self.assertIs(c._getColourObj(colour[c.CODE_KEY]), colour)

    def test_getPrefixObj(self):
        c = prompty.Colour()
        self.assertIs(c._getPrefixObj(c.BG_PREFIX), c.BG_PREFIX)
        self.assertIs(c._getPrefixObj("hi_foreground"), c.HIFG_PREFIX)
        self.assertIs(c._getPrefixObj("b"), c.EM_PREFIX)
        for prefix in c.PREFIXES:
            self.assertIs(c._getPrefixObj(prefix), prefix)
            self.assertIs(c._getPrefixObj(prefix[c.NAME_KEY]), prefix)
            self.assertIs(c._getPrefixObj(prefix[c.CODE_KEY]), prefix)

    def test_stopColour(self):
        c = prompty.Colour()
        self.assertEqual(c.stopColour(), "\[\033[0m\]")
        self.assertEqual(c.stopColour(False), "\033[0m")

    def test_startColour(self):
        c = prompty.Colour()
        self.assertEqual(c.startColour("green"), "\[\033[0;32m\]")
        self.assertEqual(c.startColour("green", wrap=False), "\033[0;32m")
        self.assertEqual(c.startColour("red","b"), "\[\033[1;31m\]")

class LexerTests(unittest.TestCase):
    def test_singleStringLiteral(self):
        l = prompty.Lexer(r"literal")
        self.assertEqual(r"literal", l.get_token())

    def test_multipleStringLiteral(self):
        l = prompty.Lexer(r"multiple string literals")
        self.assertEqual(r"multiple", l.get_token())
        self.assertEqual(r"string", l.get_token())
        self.assertEqual(r"literals", l.get_token())

    def test_stringLiteralsWithComplexChars(self):
        l = prompty.Lexer(r"complexChars:;#~@-_=+*/?'!$^&()|<>")
        self.assertEqual(r"complexChars:;#~@-_=+*/?'!$^&()|<>", l.get_token())

    def test_doubleQuoteTest(self):
        l = prompty.Lexer(r'complexChars"')
        self.assertEqual(r'complexChars"', l.get_token())

    def test_contstantQualifier(self):
        l = prompty.Lexer(r"\user")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"user", l.get_token())


class ParserTests(unittest.TestCase):
    def test_stringLiteral(self):
        p = prompty.Parser()
        self.assertEqual(r"literal", p.parse(r"literal"))

    def test_stringLiteralComplicated(self):
        p = prompty.Parser()
        self.assertEqual(r"literal-With$omeUne*pectedC#ars", p.parse(r"literal-With$omeUne*pectedC#ars"))

#     def test_definedConstant(self):
#         p = prompty.Parser()
#         self.assertEqual(r"\user", p.parse(r"\u"))



class PromptTests(unittest.TestCase):
    def test_create(self):
        p = prompty.Prompt()
        self.assertIsInstance(p, prompty.Prompt)

    def test_getPrompt(self):
        p = prompty.Prompt()
        s = p.getPrompt()
        self.assertIsInstance(s, basestring)
        self.assertGreater(len(s), 0)

#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    sys.exit(unittest.main())
