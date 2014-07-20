#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import os
import imp
import getpass
import socket
import unittest
from contextlib import contextmanager
from StringIO import StringIO

# Add base directory to path so that it can find the prompty package
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), "..")]

import prompty

prompty_bin = imp.load_source("prompty_bin", os.path.join(os.path.dirname(__file__), "..", "bin", "prompty"))


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
            ret = prompty_bin.main(argv)

        self.assertEqual(out.getvalue(), "")
        self.assertGreater(len(err.getvalue()), 0)
        self.assertEqual(ret, 0)

    def test_bash(self):
        argv = ["","-b"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertTrue(out.getvalue().startswith("export PS1"))
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

    def test_prompry(self):
        argv = ["", "1"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertGreater(len(out.getvalue()), 0)
        self.assertEqual(len(err.getvalue()), 0)
        self.assertEqual(ret, 1)


class ColourTests(unittest.TestCase):
    def test_getColourObj(self):
        self.assertIs(prompty.colours._getColourObj(prompty.colours.RED), prompty.colours.RED)
        self.assertIs(prompty.colours._getColourObj("black"), prompty.colours.BLACK)
        self.assertIs(prompty.colours._getColourObj("m"), prompty.colours.MAGENTA)
        for colour in prompty.colours.COLOURS:
            self.assertIs(prompty.colours._getColourObj(colour), colour)
            self.assertIs(prompty.colours._getColourObj(colour[prompty.colours.NAME_KEY]), colour)
            self.assertIs(prompty.colours._getColourObj(colour[prompty.colours.CODE_KEY]), colour)
 
    def test_getPrefixObj(self):
        self.assertIs(prompty.colours._getPrefixObj(prompty.colours.BG_PREFIX), prompty.colours.BG_PREFIX)
        self.assertIs(prompty.colours._getPrefixObj("hi_foreground"), prompty.colours.HIFG_PREFIX)
        self.assertIs(prompty.colours._getPrefixObj("b"), prompty.colours.EM_PREFIX)
        for prefix in prompty.colours.PREFIXES:
            self.assertIs(prompty.colours._getPrefixObj(prefix), prefix)
            self.assertIs(prompty.colours._getPrefixObj(prefix[prompty.colours.NAME_KEY]), prefix)
            self.assertIs(prompty.colours._getPrefixObj(prefix[prompty.colours.CODE_KEY]), prefix)
 
    def test_stopColour(self):
        self.assertEqual(prompty.colours.stopColour(None), "\001\033[0m\002")
        self.assertEqual(prompty.colours.stopColour(None, False), "\033[0m")
 
    def test_startColour(self):
        self.assertEqual(prompty.colours.startColour(None, "green"), "\001\033[0;32m\002")
        self.assertEqual(prompty.colours.startColour(None, "green", wrap=False), "\033[0;32m")
        self.assertEqual(prompty.colours.startColour(None, "red","b"), "\001\033[1;31m\002")
 
    def test_dynamicColourWrappers(self):
        prompty.colours._populateFunctions(sys.modules[__name__])
        self.assertEqual(sys.modules[__name__].green(None, "I'm green"), "\001\033[0;32m\002I'm green\001\033[0m\002")


class LexerTests(unittest.TestCase):
    def test_singleStringLiteral(self):
        l = prompty.lexer.Lexer(r"literal")
        self.assertEqual(r"literal", l.get_token())

    def test_multipleStringLiteral(self):
        l = prompty.lexer.Lexer(r"multiple string literals")
        self.assertEqual(r"multiple", l.get_token())
        self.assertEqual(r"string", l.get_token())
        self.assertEqual(r"literals", l.get_token())

    def test_stringLiteralsWithComplexChars(self):
        l = prompty.lexer.Lexer(r"complexChars:;#~@-_=+*/?'!$^&()|<>")
        self.assertEqual(r"complexChars:;#~@-_=+*/?'!$^&()|<>", l.get_token())

    def test_doubleQuoteTest(self):
        l = prompty.lexer.Lexer(r'complexChars"')
        self.assertEqual(r'complexChars"', l.get_token())

    def test_contstantQualifier(self):
        l = prompty.lexer.Lexer(r"\user")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"user", l.get_token())

    def test_functionArgsQualifier(self):
        l = prompty.lexer.Lexer(r"\green{literal}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_functionMultipleArgsQualifier(self):
        l = prompty.lexer.Lexer(r"\green{literal}{another}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"another", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_functionOptionalArgsQualifier(self):
        l = prompty.lexer.Lexer(r"\green[bold]{literal}")
        self.assertEqual("\\", l.get_token())
        self.assertEqual(r"green", l.get_token())
        self.assertEqual(r"[", l.get_token())
        self.assertEqual(r"bold", l.get_token())
        self.assertEqual(r"]", l.get_token())
        self.assertEqual(r"{", l.get_token())
        self.assertEqual(r"literal", l.get_token())
        self.assertEqual(r"}", l.get_token())

    def test_whitespace(self):
        l = prompty.lexer.Lexer(r"1 2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.lexer.Lexer(r"1    2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.lexer.Lexer("1\n\n\n2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.lexer.Lexer("1\t\t\t2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())
        l = prompty.lexer.Lexer("1 \t \n \t\t \n\t2")
        self.assertEqual("1", l.get_token())
        self.assertEqual("2", l.get_token())

    def test_comments(self):
        l = prompty.lexer.Lexer(r"% no comment")
        self.assertEqual("", l.get_token())
        l = prompty.lexer.Lexer(r"before% no comment")
        self.assertEqual("before", l.get_token())
        l = prompty.lexer.Lexer(r"before % no comment")
        self.assertEqual("before", l.get_token())
        l = prompty.lexer.Lexer("before% no comment\nafter")
        self.assertEqual("before", l.get_token())
        self.assertEqual("after", l.get_token())


class ParserTests(unittest.TestCase):
    def test_stringLiteral(self):
        p = prompty.parser.Parser()
        self.assertListEqual([{'type': 'literal', 'value': r"literalvalue"}],
                             p.parse("literalvalue"))

    def test_stringLiteralComplicated(self):
        p = prompty.parser.Parser()
        self.assertListEqual([{'type': 'literal', 
                               'value':r"literal-With$omeUne*pectedC#ars.,"}],
                             p.parse(r"literal-With$omeUne*pectedC#ars.,"))
  
    def test_multipleStringLiteral(self):
        p = prompty.parser.Parser()
        self.assertListEqual([{'type': 'literal', 'value': r"literal"},
                              {'type': 'literal', 'value': r"strings"},
                              {'type': 'literal', 'value': r"are"},
                              {'type': 'literal', 'value': r"concatenated"}], 
                             p.parse(r"literal strings are concatenated"))
  
    def test_functionNoArgument(self):
        p = prompty.parser.Parser()
        self.assertListEqual([{'type': 'function', 'name': r"user"}],
                             p.parse(r"\user"))
  
    def test_multipleFunctionNoArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user\hostname"))
        self.assertEqual([{'type': 'function', 'name': r"user"},
                          {'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user \hostname"))
 
    def test_functionEmptyArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse(r"\user{}"))
        self.assertEqual([{'type': 'function', 'name': r"user", 'args': [[]]},
                          {'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse(r"\user{}\user{}"))
        self.assertEqual([{'type': 'function', 'name': r"user", 'args': [[]]},
                          {'type': 'function', 'name': r"hostname", 'args': [[]]},
                          {'type': 'literal', 'value': r"otherstuff"}],
                         p.parse(r"\user{}\hostname{}otherstuff"))
 
    def test_functionNoArgumentAndLiterals(self):
        p = prompty.parser.Parser()
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
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"hello"}]]
                          }],
                         p.parse(r"\green{hello}"))
 
    def test_functionWithLiteralArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]]
                          }],
                         p.parse(r"\green{\user}"))
 
    def test_functionWithMultipleLiteralArgument(self):
        p = prompty.parser.Parser()
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
        p = prompty.parser.Parser()
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

    def test_functionWithEmptyFirstArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"range", 'args': 
                                [[],
                                 [{'type': 'literal', 'value': r"2"}]]
                          }],
                         p.parse(r"\range{}{2}"))

    def test_functionWithOptionalLiteralArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }],
                         p.parse(r"\green[bold]{\user}"))

    def test_functionWithMultipleOptionalArguments(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}],
                                            [{'type': 'function', 'name': r"bg"}]]
                          }],
                         p.parse(r"\green[bold][\bg]{\user}"))


class CompilerTests(unittest.TestCase):
    user=getpass.getuser()
    host=socket.gethostname()

    def test_singleLiteral(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"literalvalue", c.compile([{'type': 'literal', 'value': r"literalvalue"}]) )

    def test_multipleLiteral(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"literalvalue", c.compile([{'type': 'literal', 'value': r"literal"},
                                                      {'type': 'literal', 'value': r"value"}]) )

    def test_singleFunction(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(CompilerTests.user, c.compile([{'type': 'function', 'name': r"user"}]) )

    def test_nestedFunction(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[0;32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                     [[{'type': 'function', 'name': r"user"}]]}]) )

    def test_functionWithMultipleLiteralArgument(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[0;32m\002a%sb%s\001\033[0m\002" % (CompilerTests.user,CompilerTests.host),
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"a"},
                                 {'type': 'function', 'name': r"user"},
                                 {'type': 'literal', 'value': r"b"},
                                 {'type': 'function', 'name': r"hostnamefull"}]]
                          }]) )

    def test_nestedFunctionOptionalArg(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[1;32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }]) )


    def test_multipleAruments(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"2", c.compile([{'type': 'function', 'name': r"greater", 'args': 
                                           [[{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )

    def test_emptyAruments(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("..", c.compile([{'type': 'function', 'name': r"join", 'args': 
                                           [[{'type': 'literal', 'value': r"."}], 
                                            [], [], []]
                                           }]) )
        self.assertEqual(".1.2", c.compile([{'type': 'function', 'name': r"join", 'args': 
                                           [ [{'type': 'literal', 'value': r"."}]
                                            , [], [{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )

    def test_equalFunction(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("True", c.compile([{'args': [[{'type': 'literal', 'value': '1'}], 
                                                    [{'type': 'literal', 'value': '1'}]], 
                                           'type': 'function', 'name': 'equals'}]) )

def testFunc(status):
    return "This Is A Test"

def _hiddenFunc(status):
    return "This is secret"

class StandardFunctionTests(unittest.TestCase):

    def test_user(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(getpass.getuser(), c._call("user"))

    def test_hostname(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(socket.gethostname().split(".")[0], c._call("hostname"))

    def test_hostnamefull(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(socket.gethostname(), c._call("hostnamefull"))

    def test_workingdir(self):
        c = prompty.functions.FunctionContainer()
        os.chdir(os.path.expanduser("~"))
        self.assertEqual(r"~", c._call("workingdir"))
        os.chdir("/tmp")
        self.assertEqual(r"/tmp", c._call("workingdir"))

    def test_workingdirbase(self):
        c = prompty.functions.FunctionContainer()
        os.chdir("/tmp")
        self.assertEqual(r"tmp", c._call("workingdirbase"))
        os.chdir("/usr/local")
        self.assertEqual(r"local", c._call("workingdirbase"))

    def test_dollar(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(ur"$", c._call("dollar"))
        self.assertEqual(ur"#", c._call("dollar",0))

    def test_newline(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(u"\n", c._call("newline"))

    def test_return(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(u"\r", c._call("carriagereturn"))

    def test_extendFunctionContainer(self):
        c = prompty.functions.FunctionContainer()
        # Import this module
        c._addFunctions(sys.modules[__name__])
        self.assertEqual(r"This Is A Test", c._call("testFunc"))
        self.assertRaises(KeyError, c._call, "_hiddenFunc")


class ExpressionFunctionTests(unittest.TestCase):
    def test_equal(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual(True, c._call("equals","1","1"))

    def test_if(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual("1", c._call("ifexpr","True","1","2"))
        self.assertEqual("2", c._call("ifexpr","False","1","2"))
        self.assertEqual("1", c._call("ifexpr","True","1"))
        self.assertEqual("", c._call("ifexpr","0","1"))
        self.assertEqual("1", c._call("ifexpr","1","1"))

    def test_exitSuccess(self):
        c = prompty.functions.FunctionContainer(prompty.prompty.Status(0))
        self.assertEqual(True, c._call("exitsuccess"))
        c = prompty.functions.FunctionContainer(prompty.prompty.Status(1))
        self.assertEqual(False, c._call("exitsuccess"))


class ColourFunctionTests(unittest.TestCase):
    def test_colourLiteral(self):
        c = prompty.functions.FunctionContainer()
        self.assertEqual("\001\033[0;32m\002I'm green\001\033[0m\002",  c._call("green","I'm green"))
        self.assertEqual("\001\033[0;31m\002I'm red\001\033[0m\002",    c._call("red","I'm red"))


class PromptTests(unittest.TestCase):
    def test_create(self):
        p = prompty.prompty.Prompt(prompty.prompty.Status())
        self.assertIsInstance(p, prompty.prompty.Prompt)
 
    def test_getPrompt(self):
        p = prompty.prompty.Prompt(prompty.prompty.Status())
        s = p.getPrompt()
        self.assertIsInstance(s, basestring)
        self.assertGreater(len(s), 0)


class UserDirTests(unittest.TestCase):
    def test_userDirLocation(self):
        u = prompty.userdir.UserDir()
        self.assertEquals(os.path.join(os.path.expanduser('~'),prompty.userdir.PROMPTY_USER_DIR), u.getDir())



#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    sys.exit(unittest.main())