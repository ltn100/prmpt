#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import socket
import getpass

from test_prompty import UnitTestWrapper
from test_prompty import prompty


class LexerTests(UnitTestWrapper):
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


class ParserTests(UnitTestWrapper):
    def test_stringLiteral(self):
        p = prompty.parser.Parser()
        self.assertSequenceEqual([{'lineno': 1, 'type': 'literal', 'value': r"literalvalue"}],
                             p.parse("literalvalue"))

    def test_lineNumber(self):
        p = prompty.parser.Parser()
        self.assertSequenceEqual([{'lineno': 3, 'type': 'literal', 'value': r"literalvalue"}],
                             p.parse("\n\nliteralvalue"))
        self.assertSequenceEqual([{'lineno': 3, 'type': 'literal', 'value': r"literalvalue"},
                              {'lineno': 4, 'type': 'function', 'name': r"space"},
                              {'lineno': 5, 'type': 'function', 'name': r"red", 'args': 
                                [[{'lineno': 5, 'type': 'literal', 'value': r"test"}]]
                                }],
                             p.parse("%%%%\n\nliteralvalue\n\space\n\\red{test}"))

    def test_stringLiteralComplicated(self):
        p = prompty.parser.Parser()
        self.assertSequenceEqual([{'lineno': 1, 'type': 'literal', 
                               'value':r"literal-With$omeUne*pectedC#ars.,"}],
                             p.parse(r"literal-With$omeUne*pectedC#ars.,"))
  
    def test_multipleStringLiteral(self):
        p = prompty.parser.Parser()
        self.assertSequenceEqual([{'lineno': 1, 'type': 'literal', 'value': r"literal"},
                              {'lineno': 1, 'type': 'literal', 'value': r"strings"},
                              {'lineno': 1, 'type': 'literal', 'value': r"are"},
                              {'lineno': 1, 'type': 'literal', 'value': r"concatenated"}], 
                             p.parse(r"literal strings are concatenated"))
  
    def test_functionNoArgument(self):
        p = prompty.parser.Parser()
        self.assertSequenceEqual([{'lineno': 1, 'type': 'function', 'name': r"user"}],
                             p.parse(r"\user"))
  
    def test_multipleFunctionNoArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user\hostname"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'function', 'name': r"hostname"}],
                         p.parse(r"\user \hostname"))
 
    def test_functionEmptyArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse(r"\user{}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]},
                          {'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse(r"\user{}\user{}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]},
                          {'lineno': 1, 'type': 'function', 'name': r"hostname", 'args': [[]]},
                          {'lineno': 1, 'type': 'literal', 'value': r"otherstuff"}],
                         p.parse(r"\user{}\hostname{}otherstuff"))
 
    def test_functionNoArgumentAndLiterals(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"}],
                         p.parse(r"a\user"))
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"b"}],
                         p.parse(r"a\user b"))
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"b"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"c"},
                          {'lineno': 1, 'type': 'literal', 'value': r"d"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"}],
                         p.parse(r"a\user b\user c d    \user"))
 
    def test_functionWithArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'literal', 'value': r"hello"}]]
                          }],
                         p.parse(r"\green{hello}"))
 
    def test_functionWithLiteralArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'function', 'name': r"user"}]]
                          }],
                         p.parse(r"\green{\user}"))
 
    def test_functionWithMultipleLiteralArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'function', 'name': r"user"},
                                 {'lineno': 1, 'type': 'function', 'name': r"hostname"}]]
                          }],
                         p.parse(r"\green{\user\hostname}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'literal', 'value': r"a"},
                                 {'lineno': 1, 'type': 'function', 'name': r"user"},
                                 {'lineno': 1, 'type': 'literal', 'value': r"b"},
                                 {'lineno': 1, 'type': 'function', 'name': r"hostname"}]]
                          }],
                         p.parse(r"\green{a\user b\hostname}"))

    def test_functionWithMultipleArguments(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"range", 'args': 
                                [[{'lineno': 1, 'type': 'literal', 'value': r"1"}],
                                 [{'lineno': 1, 'type': 'literal', 'value': r"2"}]]
                          }],
                         p.parse(r"\range{1}{2}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"range", 'args': 
                                [[{'lineno': 1, 'type': 'literal', 'value': r"1"}],
                                 [{'lineno': 1, 'type': 'literal', 'value': r"2"},
                                  {'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                   [[{'lineno': 1, 'type': 'function', 'name': r"hostname"}]]}]]
                          }],
                         p.parse(r"\range{1}{2\green{\hostname}}"))

    def test_functionWithEmptyFirstArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"range", 'args': 
                                [[],
                                 [{'lineno': 1, 'type': 'literal', 'value': r"2"}]]
                          }],
                         p.parse(r"\range{}{2}"))

    def test_functionWithOptionalLiteralArgument(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'lineno': 1, 'type': 'literal', 'value': r"bold"}]]
                          }],
                         p.parse(r"\green[bold]{\user}"))

    def test_functionWithMultipleOptionalArguments(self):
        p = prompty.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args': 
                                [[{'lineno': 1, 'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'lineno': 1, 'type': 'literal', 'value': r"bold"}],
                                            [{'lineno': 1, 'type': 'function', 'name': r"bg"}]]
                          }],
                         p.parse(r"\green[bold][\bg]{\user}"))


class OutputTests(UnitTestWrapper):
    def test_outputString(self):
        o = prompty.compiler.Output()
        o.add("four")
        self.assertEqual("four", o.output)

    def test_outputStringLenSimple(self):
        o = prompty.compiler.Output()
        o.add("four")
        self.assertEqual(4, o.pos.column)

    def test_outputStringLenNonPrinting(self):
        o = prompty.compiler.Output()
        o.add("\001\033[31m\002red4\001\033[0m\002")
        self.assertEqual(4, o.pos.column)
        o = prompty.compiler.Output()
        o.add("\001\033[31m\002red4\001\033[0m\002four")
        self.assertEqual(8, o.pos.column)


class CompilerTests(UnitTestWrapper):
    user=getpass.getuser()
    host=socket.gethostname()
    
    def test_external(self):
        c = prompty.compiler.Compiler()
        c.compile("literal1")
        self.assertEqual(r"literal1", c.execute() )
        c.compile("literal2")
        self.assertEqual(r"literal1literal2", c.execute() )

    def test_statusLength(self):
        funcs = prompty.functionContainer.FunctionContainer()
        c = prompty.compiler.Compiler(funcs)
        c.compile("literal1")
        c.execute()
        self.assertEqual(8, funcs.status.pos.column )
        self.assertEqual(0, funcs.status.pos.row )

    def test_statusLength2(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        c.compile(r"a b\newline")
        c.execute()
        self.assertEqual(0, funcs.status.pos.column )
        self.assertEqual(1, funcs.status.pos.row )

    def test_singleLiteral(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual(r"literalvalue", c._execute([{'type': 'literal', 'value': r"literalvalue"}]) )

    def test_multipleLiteral(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual(r"literalvalue", c._execute([{'type': 'literal', 'value': r"literal"},
                                                      {'type': 'literal', 'value': r"value"}]) )

    def test_singleFunction(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual(CompilerTests.user, c._execute([{'type': 'function', 'name': r"user"}]) )

    def test_nestedFunction(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        funcs.addFunctionsFromModule(prompty.colours)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual("\001\033[32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                     [[{'type': 'function', 'name': r"user"}]]}]) )

    def test_functionWithMultipleLiteralArgument(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        funcs.addFunctionsFromModule(prompty.colours)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual("\001\033[32m\002a%sb%s\001\033[0m\002" % (CompilerTests.user,CompilerTests.host),
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"a"},
                                 {'type': 'function', 'name': r"user"},
                                 {'type': 'literal', 'value': r"b"},
                                 {'type': 'function', 'name': r"hostnamefull"}]]
                          }]) )

    def test_nestedFunctionOptionalArg(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        funcs.addFunctionsFromModule(prompty.colours)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual("\001\033[1;32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }]) )


    def test_multipleAruments(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual(r"2", c._execute([{'type': 'function', 'name': r"greater", 'args': 
                                           [[{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )

    def test_emptyAruments(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual("..", c._execute([{'type': 'function', 'name': r"join", 'args': 
                                           [[{'type': 'literal', 'value': r"."}], 
                                            [], [], []]
                                           }]) )
        self.assertEqual(".1.2", c._execute([{'type': 'function', 'name': r"join", 'args': 
                                           [ [{'type': 'literal', 'value': r"."}]
                                            , [], [{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )

    def test_equalFunction(self):
        funcs = prompty.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prompty.functions)
        funcs.addFunctionsFromModule(prompty.colours)
        c = prompty.compiler.Compiler(funcs)
        self.assertEqual("True", c._execute([{'args': [[{'type': 'literal', 'value': '1'}], 
                                                    [{'type': 'literal', 'value': '1'}]], 
                                           'type': 'function', 'name': 'equals'}]) )
