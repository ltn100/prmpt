#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import socket
import getpass

from test import prmpt
from test import UnitTestWrapper


class LexerTests(UnitTestWrapper):
    def test_singleStringLiteral(self):
        lex = prmpt.lexer.Lexer(r"literal")
        self.assertEqual(r"literal", lex.get_token())

    def test_multipleStringLiteral(self):
        lex = prmpt.lexer.Lexer(r"multiple string literals")
        self.assertEqual(r"multiple", lex.get_token())
        self.assertEqual(r"string", lex.get_token())
        self.assertEqual(r"literals", lex.get_token())

    def test_stringLiteralsWithComplexChars(self):
        lex = prmpt.lexer.Lexer(r"complexChars:;#~@-_=+*/?'!$^&()|<>")
        self.assertEqual(r"complexChars:;#~@-_=+*/?'!$^&()|<>", lex.get_token())

    def test_doubleQuoteTest(self):
        lex = prmpt.lexer.Lexer(r'complexChars"')
        self.assertEqual(r'complexChars"', lex.get_token())

    def test_contstantQualifier(self):
        lex = prmpt.lexer.Lexer("\\user")
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(r"user", lex.get_token())

    def test_functionArgsQualifier(self):
        lex = prmpt.lexer.Lexer(r"\green{literal}")
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(r"green", lex.get_token())
        self.assertEqual(r"{", lex.get_token())
        self.assertEqual(r"literal", lex.get_token())
        self.assertEqual(r"}", lex.get_token())

    def test_functionMultipleArgsQualifier(self):
        lex = prmpt.lexer.Lexer(r"\green{literal}{another}")
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(r"green", lex.get_token())
        self.assertEqual(r"{", lex.get_token())
        self.assertEqual(r"literal", lex.get_token())
        self.assertEqual(r"}", lex.get_token())
        self.assertEqual(r"{", lex.get_token())
        self.assertEqual(r"another", lex.get_token())
        self.assertEqual(r"}", lex.get_token())

    def test_functionOptionalArgsQualifier(self):
        lex = prmpt.lexer.Lexer(r"\green[bold]{literal}")
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(r"green", lex.get_token())
        self.assertEqual(r"[", lex.get_token())
        self.assertEqual(r"bold", lex.get_token())
        self.assertEqual(r"]", lex.get_token())
        self.assertEqual(r"{", lex.get_token())
        self.assertEqual(r"literal", lex.get_token())
        self.assertEqual(r"}", lex.get_token())

    def test_whitespace(self):
        lex = prmpt.lexer.Lexer(r"1 2")
        self.assertEqual("1", lex.get_token())
        self.assertEqual("2", lex.get_token())
        lex = prmpt.lexer.Lexer(r"1    2")
        self.assertEqual("1", lex.get_token())
        self.assertEqual("2", lex.get_token())
        lex = prmpt.lexer.Lexer("1\n\n\n2")
        self.assertEqual("1", lex.get_token())
        self.assertEqual("2", lex.get_token())
        lex = prmpt.lexer.Lexer("1\t\t\t2")
        self.assertEqual("1", lex.get_token())
        self.assertEqual("2", lex.get_token())
        lex = prmpt.lexer.Lexer("1 \t \n \t\t \n\t2")
        self.assertEqual("1", lex.get_token())
        self.assertEqual("2", lex.get_token())

    def test_comments(self):
        lex = prmpt.lexer.Lexer(r"% no comment")
        self.assertEqual("", lex.get_token())
        lex = prmpt.lexer.Lexer(r"before% no comment")
        self.assertEqual("before", lex.get_token())
        lex = prmpt.lexer.Lexer(r"before % no comment")
        self.assertEqual("before", lex.get_token())
        lex = prmpt.lexer.Lexer("before% no comment\nafter")
        self.assertEqual("before", lex.get_token())
        self.assertEqual("after", lex.get_token())

    def test_fixComments(self):
        i = "% comment"
        o = " % comment"
        self.assertEqual(o, prmpt.lexer.Lexer.fixComments(i))
        i = "A% comment\nB"
        o = "A % comment\nB"
        self.assertEqual(o, prmpt.lexer.Lexer.fixComments(i))
        i = "% comment\nB %comment\n%comment"
        o = " % comment\nB  %comment\n %comment"
        self.assertEqual(o, prmpt.lexer.Lexer.fixComments(i))
        i = "\\myfunc{% comment\n\targ% comment\n}% comment"
        o = "\\myfunc{ % comment\n\targ % comment\n} % comment"
        self.assertEqual(o, prmpt.lexer.Lexer.fixComments(i))

    def test_fixLineNumbers(self):
        i = "% comment"
        o = i
        self.assertEqual(o, prmpt.lexer.Lexer.fixLineNumbers(i))
        i = "% comment\n"
        o = "% comment \n"
        self.assertEqual(o, prmpt.lexer.Lexer.fixLineNumbers(i))
        i = "\nA\nB"
        o = " \nA \nB"
        self.assertEqual(o, prmpt.lexer.Lexer.fixLineNumbers(i))
        i = "\r\nA\r\nB"
        o = " \r\nA \r\nB"
        self.assertEqual(o, prmpt.lexer.Lexer.fixLineNumbers(i))
        i = " \nA \nB"
        o = "  \nA  \nB"
        self.assertEqual(o, prmpt.lexer.Lexer.fixLineNumbers(i))

    def test_lineNumbers(self):
        s = r"""% Comment (line 1)
            line2

            line4%comment immediately following
            \myfunction{} %comment on line 5

            % Blank line 7 comment
            \function{% comment following {
                \green{line}
            }
            % end of file comment"""
        lex = prmpt.lexer.Lexer(s)
        self.assertEqual("line2", lex.get_token())
        self.assertEqual(2, lex.lineno)
        self.assertEqual("line4", lex.get_token())
        self.assertEqual(4, lex.lineno)
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(5, lex.lineno)
        self.assertEqual("myfunction", lex.get_token())
        self.assertEqual(5, lex.lineno)
        self.assertEqual("{", lex.get_token())
        self.assertEqual(5, lex.lineno)
        self.assertEqual("}", lex.get_token())
        self.assertEqual(5, lex.lineno)
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(8, lex.lineno)
        self.assertEqual("function", lex.get_token())
        self.assertEqual(8, lex.lineno)
        self.assertEqual("{", lex.get_token())
        self.assertEqual(8, lex.lineno)
        self.assertEqual("\\", lex.get_token())
        self.assertEqual(9, lex.lineno)
        self.assertEqual("green", lex.get_token())
        self.assertEqual(9, lex.lineno)
        self.assertEqual("{", lex.get_token())
        self.assertEqual(9, lex.lineno)
        self.assertEqual("line", lex.get_token())
        self.assertEqual(9, lex.lineno)
        self.assertEqual("}", lex.get_token())
        self.assertEqual(9, lex.lineno)
        self.assertEqual("}", lex.get_token())
        self.assertEqual(10, lex.lineno)
        self.assertFalse(lex.get_token())


class ParserTests(UnitTestWrapper):
    def test_stringLiteral(self):
        p = prmpt.parser.Parser()
        self.assertSequenceEqual(
            [{'lineno': 1, 'type': 'literal', 'value': r"literalvalue"}],
            p.parse("literalvalue")
        )

    def test_lineNumber(self):
        p = prmpt.parser.Parser()
        self.assertSequenceEqual(
            [{'lineno': 3, 'type': 'literal', 'value': r"literalvalue"}],
            p.parse("\n\nliteralvalue")
        )
        self.assertSequenceEqual(
            [
                {'lineno': 3, 'type': 'literal', 'value': r"literalvalue"},
                {'lineno': 4, 'type': 'function', 'name': r"space"},
                {'lineno': 5, 'type': 'function', 'name': r"red", 'args': [
                    [{'lineno': 5, 'type': 'literal', 'value': r"test"}]
                ]}
            ],
            p.parse("%%%%\n\nliteralvalue\n\\space\n\\red{test}")
        )

    def test_stringLiteralComplicated(self):
        p = prmpt.parser.Parser()
        self.assertSequenceEqual(
            [{'lineno': 1, 'type': 'literal', 'value': r"literal-With$omeUne*pectedC#ars.,"}],
            p.parse(r"literal-With$omeUne*pectedC#ars.,")
        )

    def test_multipleStringLiteral(self):
        p = prmpt.parser.Parser()
        self.assertSequenceEqual(
            [
                {'lineno': 1, 'type': 'literal', 'value': r"literal"},
                {'lineno': 1, 'type': 'literal', 'value': r"strings"},
                {'lineno': 1, 'type': 'literal', 'value': r"are"},
                {'lineno': 1, 'type': 'literal', 'value': r"concatenated"}
            ],
            p.parse(r"literal strings are concatenated")
        )

    def test_functionNoArgument(self):
        p = prmpt.parser.Parser()
        self.assertSequenceEqual([{'lineno': 1, 'type': 'function', 'name': r"user"}],
                                 p.parse("\\user"))

    def test_multipleFunctionNoArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'function', 'name': r"hostname"}],
                         p.parse("\\user\\hostname"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'function', 'name': r"hostname"}],
                         p.parse("\\user \\hostname"))

    def test_functionEmptyArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse("\\user{}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]},
                          {'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]}],
                         p.parse("\\user{}\\user{}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"user", 'args': [[]]},
                          {'lineno': 1, 'type': 'function',
                              'name': r"hostname", 'args': [[]]},
                          {'lineno': 1, 'type': 'literal', 'value': r"otherstuff"}],
                         p.parse("\\user{}\\hostname{}otherstuff"))

    def test_functionNoArgumentAndLiterals(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"}],
                         p.parse("a\\user"))
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"b"}],
                         p.parse("a\\user b"))
        self.assertEqual([{'lineno': 1, 'type': 'literal', 'value': r"a"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"b"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"},
                          {'lineno': 1, 'type': 'literal', 'value': r"c"},
                          {'lineno': 1, 'type': 'literal', 'value': r"d"},
                          {'lineno': 1, 'type': 'function', 'name': r"user"}],
                         p.parse("a\\user b\\user c d    \\user"))

    def test_functionWithArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'literal', 'value': r"hello"}]]
                           }],
                         p.parse(r"\green{hello}"))

    def test_functionWithLiteralArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'function', 'name': r"user"}]]
                           }],
                         p.parse("\\green{\\user}"))

    def test_functionWithMultipleLiteralArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'function', 'name': r"user"},
                             {'lineno': 1, 'type': 'function', 'name': r"hostname"}]]
                           }],
                         p.parse("\\green{\\user\\hostname}"))
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'literal', 'value': r"a"},
                             {'lineno': 1, 'type': 'function', 'name': r"user"},
                             {'lineno': 1, 'type': 'literal', 'value': r"b"},
                             {'lineno': 1, 'type': 'function', 'name': r"hostname"}]]
                           }],
                         p.parse("\\green{a\\user b\\hostname}"))

    def test_functionWithMultipleArguments(self):
        p = prmpt.parser.Parser()
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
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"range", 'args':
                           [[],
                            [{'lineno': 1, 'type': 'literal', 'value': r"2"}]]
                           }],
                         p.parse(r"\range{}{2}"))

    def test_functionWithOptionalLiteralArgument(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'function', 'name': r"user"}]],
                           'optargs': [[{'lineno': 1, 'type': 'literal', 'value': r"bold"}]]
                           }],
                         p.parse("\\green[bold]{\\user}"))

    def test_functionWithMultipleOptionalArguments(self):
        p = prmpt.parser.Parser()
        self.assertEqual([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                           [[{'lineno': 1, 'type': 'function', 'name': r"user"}]],
                           'optargs': [[{'lineno': 1, 'type': 'literal', 'value': r"bold"}],
                                       [{'lineno': 1, 'type': 'function', 'name': r"bg"}]]
                           }],
                         p.parse("\\green[bold][\\bg]{\\user}"))


class CompilerTests(UnitTestWrapper):
    user = getpass.getuser()
    host = socket.gethostname()

    def test_external(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        c = prmpt.compiler.Compiler(funcs)
        c.compile("literal1")
        self.assertEqual(r"literal1", c.execute())
        c.compile("literal2")
        self.assertEqual(r"literal1literal2", c.execute())

    def test_statusLength(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        c = prmpt.compiler.Compiler(funcs)
        c.compile("literal1")
        c.execute()
        self.assertEqual(8, funcs.status.pos.column)
        self.assertEqual(0, funcs.status.pos.row)

    def test_statusLength2(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        c.compile(r"a b\newline")
        c.execute()
        self.assertEqual(0, funcs.status.pos.column)
        self.assertEqual(1, funcs.status.pos.row)

    def test_singleLiteral(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual(r"literalvalue", c._execute(
            [{'lineno': 1, 'type': 'literal', 'value': r"literalvalue"}]))

    def test_multipleLiteral(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual(r"literalvalue", c._execute([{'lineno': 1, 'type': 'literal', 'value': r"literal"},
                                                      {'lineno': 1, 'type': 'literal', 'value': r"value"}]))

    def test_singleFunction(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual(CompilerTests.user, c._execute(
            [{'lineno': 1, 'type': 'function', 'name': r"user"}]))

    def test_nestedFunction(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        funcs.addFunctionsFromModule(prmpt.colours)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual("\001\033[32m\002%s\001\033[0m\002" % CompilerTests.user,
                         c._execute([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                                      [[{'lineno': 1, 'type': 'function', 'name': r"user"}]]}]))

    def test_functionWithMultipleLiteralArgument(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        funcs.addFunctionsFromModule(prmpt.colours)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual("\001\033[32m\002a%sb%s\001\033[0m\002" % (CompilerTests.user, CompilerTests.host),
                         c._execute([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                                      [[{'lineno': 1, 'type': 'literal', 'value': r"a"},
                                        {'lineno': 1, 'type': 'function',
                                            'name': r"user"},
                                          {'lineno': 1, 'type': 'literal',
                                              'value': r"b"},
                                          {'lineno': 1, 'type': 'function', 'name': r"hostnamefull"}]]
                                      }]))

    def test_nestedFunctionOptionalArg(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        funcs.addFunctionsFromModule(prmpt.colours)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual("\001\033[1;32m\002%s\001\033[0m\002" % CompilerTests.user,
                         c._execute([{'lineno': 1, 'type': 'function', 'name': r"green", 'args':
                                      [[{'lineno': 1, 'type': 'function', 'name': r"user"}]],
                                      'optargs': [[{'lineno': 1, 'type': 'literal', 'value': r"bold"}]]
                                      }]))

    def test_multipleAruments(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual(r"2", c._execute([{'lineno': 1, 'type': 'function', 'name': r"max", 'args':
                                            [[{'lineno': 1, 'type': 'literal', 'value': r"1"}],
                                             [{'lineno': 1, 'type': 'literal',
                                               'value': r"2"}]
                                             ]}]))

    def test_emptyAruments(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual("..", c._execute([{'lineno': 1, 'type': 'function', 'name': r"join", 'args':
                                            [[{'lineno': 1, 'type': 'literal', 'value': r"."}],
                                             [], [], []]
                                            }]))
        self.assertEqual(".1.2", c._execute(
            [{'lineno': 1, 'type': 'function', 'name': r"join", 'args':
              [[{'lineno': 1, 'type': 'literal', 'value': r"."}], [], [{'lineno': 1, 'type': 'literal', 'value': r"1"}],
               [{'lineno': 1, 'type': 'literal',
                 'value': r"2"}]
               ]}]))

    def test_equalFunction(self):
        funcs = prmpt.functionContainer.FunctionContainer()
        funcs.addFunctionsFromModule(prmpt.functions)
        funcs.addFunctionsFromModule(prmpt.colours)
        c = prmpt.compiler.Compiler(funcs)
        self.assertEqual("True", c._execute([{'args': [[{'lineno': 1, 'type': 'literal', 'value': '1'}],
                                                       [{'lineno': 1, 'type': 'literal', 'value': '1'}]],
                                              'lineno': 1, 'type': 'function', 'name': 'equals'}]))

#    def test_position


# class OutputTests(UnitTestWrapper):
#     def test_outputString(self):
#         o = prmpt.compiler.Output()
#         o.add("four")
#         self.assertEqual("four", o.output)
#
#     def test_outputStringLenSimple(self):
#         o = prmpt.compiler.Output()
#         o.add("four")
#         self.assertEqual(4, o.pos.column)
#
#     def test_outputStringLenNonPrinting(self):
#         o = prmpt.compiler.Output()
#         o.add("\001\033[31m\002red4\001\033[0m\002")
#         self.assertEqual(4, o.pos.column)
#         o = prmpt.compiler.Output()
#         o.add("\001\033[31m\002red4\001\033[0m\002four")
#         self.assertEqual(8, o.pos.column)
