#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import os
import re
import imp
import getpass
import socket
import shutil
import tempfile
import unittest
import distutils.spawn
from contextlib import contextmanager
from StringIO import StringIO

TEST_DIR = os.path.dirname(__file__)

# Add base directory to path so that it can find the prompty package
sys.path[0:0] = [os.path.dirname(TEST_DIR)]

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
        self.assertRaises(KeyError, prompty.colours._getColourObj, "burple")
 
    def test_getPrefixObj(self):
        self.assertIs(prompty.colours._getPrefixObj(prompty.colours.NORMAL), prompty.colours.NORMAL)
        self.assertIs(prompty.colours._getPrefixObj("italic"), prompty.colours.ITALIC)
        self.assertIs(prompty.colours._getPrefixObj("b"), prompty.colours.BOLD)
        for prefix in prompty.colours.PREFIXES:
            self.assertIs(prompty.colours._getPrefixObj(prefix), prefix)
            self.assertIs(prompty.colours._getPrefixObj(prefix[prompty.colours.NAME_KEY]), prefix)
            self.assertIs(prompty.colours._getPrefixObj(prefix[prompty.colours.CODE_KEY]), prefix)
        self.assertRaises(KeyError, prompty.colours._getPrefixObj, "upsidedown")
 
    def test_stopColour(self):
        self.assertEqual(prompty.colours.stopColour(None), "\001\033[0m\002")
        self.assertEqual(prompty.colours.stopColour(None, False), "\033[0m")
 
    def test_startColour(self):
        self.assertEqual(prompty.colours.startColour(None, "green"), "\001\033[32m\002")
        self.assertEqual(prompty.colours.startColour(None, "green", wrap=False), "\033[32m")
        self.assertEqual(prompty.colours.startColour(None, "red",prefix="b"), "\001\033[1;31m\002")
        self.assertEqual(prompty.colours.startColour(None, "1"), "\001\033[38;5;1m\002")
 
    def test_dynamicColourWrappers(self):
        prompty.colours._populateFunctions(sys.modules[__name__])
        self.assertEqual(sys.modules[__name__].green(None, "I'm green"), "\001\033[32m\002I'm green\001\033[0m\002")
        self.assertEqual(sys.modules[__name__].green(None, "I'm green and bold", "bold"), "\001\033[1;32m\002I'm green and bold\001\033[0m\002")


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
        self.assertEqual("\001\033[32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c.compile([{'type': 'function', 'name': r"green", 'args': 
                                     [[{'type': 'function', 'name': r"user"}]]}]) )

    def test_functionWithMultipleLiteralArgument(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[32m\002a%sb%s\001\033[0m\002" % (CompilerTests.user,CompilerTests.host),
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

    def test_noname(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertRaises(TypeError, c._call)

    def test_user(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(getpass.getuser(), c._call("user"))

    def test_hostname(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(socket.gethostname().split(".")[0], c._call("hostname"))

    def test_hostnamefull(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(socket.gethostname(), c._call("hostnamefull"))

    def test_workingdir(self):
        origcwd = os.getcwd()
        c = prompty.functionContainer.FunctionContainer()
        os.chdir(os.path.expanduser("~"))
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(r"~", c._call("workingdir"))
        tmpDir = tempfile.mkdtemp()
        os.chdir(tmpDir)
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(tmpDir, c._call("workingdir"))
        # Cleanup
        os.chdir(origcwd)
        os.environ["PWD"] = os.getcwd()
        shutil.rmtree(tmpDir)

    def test_workingdirbase(self):
        origcwd = os.getcwd()
        c = prompty.functionContainer.FunctionContainer()
        tmpDir = tempfile.mkdtemp()
        os.chdir(tmpDir)
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(os.path.basename(tmpDir), c._call("workingdirbase"))
        os.chdir("/usr/local")
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(r"local", c._call("workingdirbase"))
        # Cleanup
        os.chdir(origcwd)
        os.environ["PWD"] = os.getcwd()
        shutil.rmtree(tmpDir)

    def test_dollar(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(ur"$", c._call("dollar"))
        self.assertEqual(ur"#", c._call("dollar",0))

    def test_specialChars(self):
        c = prompty.functionContainer.FunctionContainer()
        chars = [
                 ("newline",            u"\n"),
                 ("carriagereturn",     u"\r"),
                 ("space",              u" "),
                 ("backslash",          u"\\"),
                 ("percent",            u"%"),
                 ("opencurly",          u"{"),
                 ("closecurly",         u"}"),
                 ("opensquare",         u"["),
                 ("closesquare",        u"]"),
                 ("escape",             u"\033")
                ]
        for char in chars:
            self.assertEqual(char[1], c._call(char[0]))

    def test_extendFunctionContainer(self):
        c = prompty.functionContainer.FunctionContainer()
        # Import this module
        c.addFunctions(sys.modules[__name__])
        self.assertEqual(r"This Is A Test", c._call("testFunc"))
        self.assertRaises(KeyError, c._call, "_hiddenFunc")

    def test_date(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(bool(re.match(r"^[a-zA-z]+ [a-zA-z]+ [0-9]+$",c._call("date"))))

    def test_datefmt(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(bool(re.match(r"^[0-9:]+$",c._call("datefmt"))))
        self.assertTrue(bool(re.match(r"^hello$",c._call("datefmt","hello"))))
        self.assertTrue(bool(re.match(r"^[0-9]{2}$",c._call("datefmt","#d"))))

    def test_isRealPath(self):
        origcwd = os.getcwd()
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(c._call("isrealpath"))
        tmpDir = tempfile.mkdtemp()
        link = os.path.join(tmpDir, "link")
        os.symlink(tmpDir, link)
        os.chdir(link)
        os.environ["PWD"] = link
        self.assertFalse(c._call("isrealpath"))
        # Cleanup
        os.chdir(origcwd)
        os.environ["PWD"] = os.getcwd()
        shutil.rmtree(tmpDir)


class ExpressionFunctionTests(unittest.TestCase):
    def test_equal(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(True, c._call("equals","1","1"))

    def test_if(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual("1", c._call("ifexpr","True","1","2"))
        self.assertEqual("2", c._call("ifexpr","False","1","2"))
        self.assertEqual("1", c._call("ifexpr","True","1"))
        self.assertEqual("", c._call("ifexpr","0","1"))
        self.assertEqual("1", c._call("ifexpr","1","1"))

    def test_exitSuccess(self):
        c = prompty.functionContainer.FunctionContainer(prompty.prompty.Status(0))
        self.assertEqual(True, c._call("exitsuccess"))
        c = prompty.functionContainer.FunctionContainer(prompty.prompty.Status(1))
        self.assertEqual(False, c._call("exitsuccess"))


class ColourFunctionTests(unittest.TestCase):
    def test_colourLiteral(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual("\001\033[32m\002I'm green\001\033[0m\002",  c._call("green","I'm green"))
        self.assertEqual("\001\033[31m\002I'm red\001\033[0m\002",    c._call("red","I'm red"))


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

    def test_initialise(self):
        tmpDir = tempfile.mkdtemp()
        u = prompty.userdir.UserDir(tmpDir)
        self.assertTrue(os.path.isdir(u.getDir()))
        self.assertTrue(os.path.exists(u.getConfigFile()))
        # Cleanup
        shutil.rmtree(tmpDir)

    def test_initialiseExitst(self):
        tmpDir = tempfile.mkdtemp()
        # Create .prompty file in the way
        open(os.path.join(tmpDir, prompty.userdir.PROMPTY_USER_DIR), 'a').close()
        self.assertRaises(IOError, prompty.userdir.UserDir, tmpDir)
        # Cleanup
        shutil.rmtree(tmpDir)

    def test_copyFiles(self):
        tmpDir = tempfile.mkdtemp()
        test1 = os.path.join(tmpDir, "test1")
        test2 = os.path.join(tmpDir, "test2")
        # touch test1
        open(os.path.join(tmpDir, "test1"), 'a').close()
        prompty.userdir.UserDir.copy(test1, test2)
        self.assertTrue(os.path.exists(test2))
        self.assertRaises(IOError, prompty.userdir.UserDir.copy, "/file/doesnt/exist", test2)
        # Cleanup
        shutil.rmtree(tmpDir)


class ConfigTests(unittest.TestCase):
    def test_loadConfig(self):
        c = prompty.config.Config()
        c.load(os.path.join(os.path.dirname(TEST_DIR), 
                            prompty.userdir.SKEL_DIR, 
                            prompty.userdir.PROMPTY_CONFIG_FILE))
        self.assertEquals(os.path.join(os.path.dirname(TEST_DIR), 
                                       prompty.userdir.SKEL_DIR, 
                                       "default.prompty"), c.promptFile)

    def test_loadPrompt(self):
        c = prompty.config.Config()
        c.promptFile = os.path.join(os.path.dirname(TEST_DIR), 
                                       prompty.userdir.SKEL_DIR, 
                                       "default.prompty")
        c.loadPromptFile()
        self.assertGreater(len(c.promptString), 0)


class GitTests(unittest.TestCase):
    def test_commandAvailable(self):
        git_installed = bool(distutils.spawn.find_executable(prompty.git.GIT_COMMAND))
        g = prompty.git.Git()
        self.assertEquals(git_installed, g.installed)
        g = prompty.git.Git("bogus_command_foo")
        self.assertEquals(False, g.installed)




#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    sys.exit(unittest.main())
