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

    def test_dynamicColourWrappers(self):
        c = prompty.Colour()
        self.assertEqual(c.green("I'm green"), "\\[\033[0;32m\\]I'm green\\[\033[0m\\]")


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

    def test_functionArgsQualifier(self):
        l = prompty.Lexer(r"\green{literal}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_functionMultipleArgsQualifier(self):
        l = prompty.Lexer(r"\green{literal}{another}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"another", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_functionOptionalArgsQualifier(self):
        l = prompty.Lexer(r"\green[bold]{literal}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"[", l.get_token())
        self.assertEqual(r"bold", l.get_token())
        self.assertEqual(r"]", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_whitespace(self):
        l = prompty.Lexer(r"1 2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.Lexer(r"1    2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.Lexer("1\n\n\n2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.Lexer("1\t\t\t2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.Lexer("1 \t \n \t\t \n\t2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())

    def test_comments(self):
        l = prompty.Lexer(r"% no comment")
        self.assertEqual("", l.get_token())
        l = prompty.Lexer(r"before% no comment")
        self.assertEqual("before", l.get_token())
        l = prompty.Lexer(r"before % no comment")
        self.assertEqual("before", l.get_token())
        l = prompty.Lexer("before% no comment\nafter")
        self.assertEqual("before", l.get_token())
        self.assertEqual("after", l.get_token())


class ParserTests(unittest.TestCase):
    def test_stringLiteral(self):
        p = prompty.Parser()
        self.assertListEqual([{'type': 'literal', 'value': r"literalvalue"}],
                             p.parse("literalvalue"))

    def test_stringLiteralComplicated(self):
        p = prompty.Parser()
        self.assertListEqual([{'type': 'literal', 
                               'value':r"literal-With$omeUne*pectedC#ars.,"}],
                             p.parse(r"literal-With$omeUne*pectedC#ars.,"))
  
    def test_multipleStringLiteral(self):
        p = prompty.Parser()
        self.assertListEqual([{'type': 'literal', 'value': r"literal"},
                              {'type': 'literal', 'value': r"strings"},
                              {'type': 'literal', 'value': r"are"},
                              {'type': 'literal', 'value': r"concatenated"}], 
                             p.parse(r"literal strings are concatenated"))
  
    def test_functionNoArgument(self):
        p = prompty.Parser()
        self.assertListEqual([{'type': 'function', 'name': r"user"}],
                             p.parse(r"\user"))
  
    def test_multipleFunctionNoArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user\hostname"))
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user \hostname"))
 
    def test_functionEmptyArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"user"}],
                         p.parse(r"\user{}"))
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"user"}],
                         p.parse(r"\user{}\user{}"))
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"hostname"},
                          {'type': 'literal', 'value': r"otherstuff"}],
                         p.parse(r"\user{}\hostname{}otherstuff"))
 
    def test_functionNoArgumentAndLiterals(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'literal', 'value': r"a"},
                          {'type': 'function', 'name': r"user"}],
                         p.parse(r"a\user"))
        self.assertEqual([{'type': 'literal', 'value': r"a"},
                          {'type': 'function', 'name': r"user"},
                          {'type': 'literal', 'value': r"b"}],
                         p.parse(r"a\user b"))
        self.assertEqual([{'type': 'literal', 'value': r"a"},
                          {'type': 'function', 'name': r"user"},
                          {'type': 'literal', 'value': r"b"},
                          {'type': 'function', 'name': r"user"},
                          {'type': 'literal', 'value': r"c"},
                          {'type': 'literal', 'value': r"d"},
                          {'type': 'function', 'name': r"user"}],
                         p.parse(r"a\user b\user c d    \user"))
 
    def test_functionWithArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"hello"}]]
                          }],
                         p.parse(r"\green{hello}"))
 
    def test_functionWithLiteralArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]]
                          }],
                         p.parse(r"\green{\user}"))
 
    def test_functionWithMultipleLiteralArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"},
                                 {'type': 'function', 'name': r"hostname"}]]
                          }],
                         p.parse(r"\green{\user\hostname}"))
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"a"},
                                 {'type': 'function', 'name': r"user"},
                                 {'type': 'literal', 'value': r"b"},
                                 {'type': 'function', 'name': r"hostname"}]]
                          }],
                         p.parse(r"\green{a\user b\hostname}"))

    def test_functionWithMultipleArguments(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"range", 'args': 
                                [[{'type': 'literal', 'value': r"1"}],
                                 [{'type': 'literal', 'value': r"2"}]]
                          }],
                         p.parse(r"\range{1}{2}"))
        self.assertEqual([{'type': 'function', 'name': r"range", 'args': 
                                [[{'type': 'literal', 'value': r"1"}],
                                 [{'type': 'literal', 'value': r"2"},
                                  {'type': 'function', 'name': r"green", 'args': 
                                   [[{'type': 'function', 'name': r"hostname"}]]}]]
                          }],
                         p.parse(r"\range{1}{2\green{\hostname}}"))

    def test_functionWithOptionalLiteralArgument(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }],
                         p.parse(r"\green[bold]{\user}"))

    def test_functionWithMultipleOptionalArguments(self):
        p = prompty.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}],
                                            [{'type': 'function', 'name': r"bg"}]]
                          }],
                         p.parse(r"\green[bold][\bg]{\user}"))

class CompilerTests(unittest.TestCase):
    def test_singleLiteral(self):
        c = prompty.Compiler()
        self.assertEqual(r"literalvalue", c.compile([{'type': 'literal', 'value': r"literalvalue"}]) )

    def test_multipleLiteral(self):
        c = prompty.Compiler()
        self.assertEqual(r"literalvalue", c.compile([{'type': 'literal', 'value': r"literal"},
                                                      {'type': 'literal', 'value': r"value"}]) )

    def test_singleFunction(self):
        c = prompty.Compiler()
        self.assertEqual(r"\u", c.compile([{'type': 'function', 'name': r"user"}]) )

    def test_nestedFunction(self):
        c = prompty.Compiler()
        self.assertEqual("\\[\033[0;32m\\]\\u\\[\033[0m\\]", 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                     [[{'type': 'function', 'name': r"user"}]]}]) )

    def test_functionWithMultipleLiteralArgument(self):
        c = prompty.Compiler()
        self.assertEqual("\\[\033[0;32m\\]a\\ub\\h\\[\033[0m\\]", 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"a"},
                                 {'type': 'function', 'name': r"user"},
                                 {'type': 'literal', 'value': r"b"},
                                 {'type': 'function', 'name': r"hostname"}]]
                          }]) )

    def test_nestedFunctionOptionalArg(self):
        c = prompty.Compiler()
        self.assertEqual("\\[\033[1;32m\\]\\u\\[\033[0m\\]", 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }]) )


    def test_multipleAruments(self):
        c = prompty.Compiler()
        self.assertEqual(r"2", c.compile([{'type': 'function', 'name': r"greater", 'args': 
                                           [[{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )


class FunctionContainerTests(unittest.TestCase):
    class TestFunctions(object):
        @staticmethod
        def test():
            return "This Is A Test"
    
        @staticmethod
        def _hidden():
            return "This is secret"
    
    def test_userLiteral(self):
        c = prompty.FunctionContainer()
        self.assertEqual(c.call("user"), r"\u")

    def test_hostnameLiteral(self):
        c = prompty.FunctionContainer()
        self.assertEqual(c.call("hostname"), r"\h")

    def test_colourLiteral(self):
        c = prompty.FunctionContainer()
        self.assertEqual(c.call("green","I'm green"), "\\[\033[0;32m\\]I'm green\\[\033[0m\\]")
        self.assertEqual(c.call("red","I'm red"), "\\[\033[0;31m\\]I'm red\\[\033[0m\\]")

    def test_extendFunctionContainer(self):
        c = prompty.FunctionContainer()
        c.addFunctions(FunctionContainerTests.TestFunctions)
        self.assertEqual(c.call("test"), "This Is A Test")
        self.assertRaises(KeyError, c.call, "_hidden")

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
