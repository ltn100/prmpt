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
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


try:
    # If we are running this from the source prompty dir then use
    # the source prompty module. Otherwise try to import the system
    # installed package
    if os.path.isdir("prompty") and os.path.isdir("test"):
        sys.path[0:0] = [os.getcwd()]
    
    import prompty
    if 'colours' not in dir(prompty):
        # This will stop accidentally importing the module
        # 'prompty.py' (we want the package)
        raise ImportError
except ImportError:
    if 'prompty' in sys.modules:
        del sys.modules['prompty']
    # Add base directory to path so that it can find the prompty package
    print __file__
    print os.path.dirname(TEST_DIR)
    sys.path[0:0] = [os.path.dirname(TEST_DIR)]
    import prompty
    if 'colours' not in dir(prompty):
        # This will stop accidentally importing the module
        # 'prompty.py' (we want the package)
        raise ImportError


prompty_exec = distutils.spawn.find_executable("prompty")
if not prompty_exec:
    # If prompty not found in the system path get the version from the bin dir
    prompty_exec = os.path.join(TEST_DIR, "..", "bin", "prompty")

prompty_bin = imp.load_source("prompty_bin", prompty_exec)


_MAX_LENGTH = 80
def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'

class UnitTestWrapper(unittest.TestCase):
    """
    A wrapper for the unittest class to enable support
    for functions not available in python 2.6
    """
    pass

if True or "assertIs" not in dir(UnitTestWrapper):
    def _assertIs(self, expr1, expr2, msg=None):
        """Just like self.assertTrue(a is b), but with a nicer default message."""
        if expr1 is not expr2:
            standardMsg = '%s is not %s' % (safe_repr(expr1),
                                             safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))
    setattr(UnitTestWrapper, "assertIs", _assertIs)

if True or "assertGreater" not in dir(UnitTestWrapper):
    def _assertGreater(self, a, b, msg=None):
        """Just like self.assertTrue(a > b), but with a nicer default message."""
        if not a > b:
            standardMsg = '%s not greater than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))
    setattr(UnitTestWrapper, "assertGreater", _assertGreater)

if True or "assertIsInstance" not in dir(UnitTestWrapper):
    def _assertIsInstance(self, obj, cls, msg=None):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
        default message."""
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))
    setattr(UnitTestWrapper, "assertIsInstance", _assertIsInstance)

if True or "assertSequenceEqual" not in dir(UnitTestWrapper):
    def _assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None):
        """An equality assertion for ordered sequences (like lists and tuples).

        For the purposes of this function, a valid ordered sequence type is one
        which can be indexed, has a length, and has an equality operator.

        Args:
            seq1: The first sequence to compare.
            seq2: The second sequence to compare.
            seq_type: The expected datatype of the sequences, or None if no
                    datatype should be enforced.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException('First sequence is not a %s: %s'
                                        % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException('Second sequence is not a %s: %s'
                                        % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        if differing is None:
            if seq1 == seq2:
                return

            seq1_repr = safe_repr(seq1)
            seq2_repr = safe_repr(seq2)
            if len(seq1_repr) > 30:
                seq1_repr = seq1_repr[:30] + '...'
            if len(seq2_repr) > 30:
                seq2_repr = seq2_repr[:30] + '...'
            elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
            differing = '%ss differ: %s != %s\n' % elements

            for i in xrange(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                 (i, seq_type_name))
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                 (i, seq_type_name))
                    break

                if item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                 (i, item1, item2))
                    break
            else:
                if (len1 == len2 and seq_type is None and
                    type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                             'elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                             'elements.\n' % (seq_type_name, len2 - len1))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)
    setattr(UnitTestWrapper, "assertSequenceEqual", _assertSequenceEqual)


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MainTests(UnitTestWrapper):
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


class ColourTests(UnitTestWrapper):

    def test_getColourCode4Bit(self):
        self.assertEquals(prompty.colours.RED[prompty.colours.VAL_KEY], prompty.colours._getColourCode(prompty.colours.RED) )
        self.assertEquals(prompty.colours.BLACK[prompty.colours.VAL_KEY], prompty.colours._getColourCode("black"))
        self.assertEquals(prompty.colours.MAGENTA[prompty.colours.VAL_KEY], prompty.colours._getColourCode("m"))
        for colour in prompty.colours.COLOURS:
            self.assertEquals(colour[prompty.colours.VAL_KEY], prompty.colours._getColourCode(colour) )
            self.assertEquals(colour[prompty.colours.VAL_KEY], prompty.colours._getColourCode(colour[prompty.colours.NAME_KEY]) )
            self.assertEquals(colour[prompty.colours.VAL_KEY], prompty.colours._getColourCode(colour[prompty.colours.CODE_KEY]) )
        self.assertRaises(ValueError, prompty.colours._getColourCode, "burple")
        self.assertRaises(ValueError, prompty.colours._getColourCode, "")

    def test_getColourCodeBg4Bit(self):
        for colour in prompty.colours.COLOURS:
            self.assertEquals(int(colour[prompty.colours.VAL_KEY])+prompty.colours.BG_OFFSET, 
                              prompty.colours._getColourCode(colour,prompty.colours.BACKGROUND) )
            self.assertEquals(int(colour[prompty.colours.VAL_KEY])+prompty.colours.BG_OFFSET, 
                              prompty.colours._getColourCode(colour[prompty.colours.NAME_KEY],prompty.colours.BACKGROUND) )
            self.assertEquals(int(colour[prompty.colours.VAL_KEY])+prompty.colours.BG_OFFSET, 
                              prompty.colours._getColourCode(colour[prompty.colours.CODE_KEY],prompty.colours.BACKGROUND) )
        self.assertRaises(ValueError, prompty.colours._getColourCode, "burple")

    def test_getColourCode8Bit(self):
        self.assertEquals("38;5;145", prompty.colours._getColourCode("145") )
        self.assertEquals("38;5;0", prompty.colours._getColourCode("0") )
        self.assertEquals("38;5;255", prompty.colours._getColourCode("255") )
        self.assertRaises(ValueError, prompty.colours._getColourCode, "256")
        self.assertRaises(ValueError, prompty.colours._getColourCode, "0x456")
        self.assertEquals("38;5;16", prompty.colours._getColourCode("#000") )
        self.assertEquals("38;5;196", prompty.colours._getColourCode("#f00") )
        self.assertEquals("38;5;46", prompty.colours._getColourCode("#0f0") )
        self.assertEquals("38;5;21", prompty.colours._getColourCode("#00f") )
        self.assertRaises(ValueError, prompty.colours._getColourCode, "#bat")
        self.assertEquals("38;5;231", prompty.colours._getColourCode("#gff") )
        self.assertEquals("38;5;16", prompty.colours._getColourCode("#g00") )
        self.assertEquals("38;5;232", prompty.colours._getColourCode("#g05") )
        self.assertEquals("38;5;239", prompty.colours._getColourCode("#g4e") )
        self.assertEquals("38;5;255", prompty.colours._getColourCode("#gee") )

    def test_getColourCodeBg8Bit(self):
        self.assertEquals("48;5;145", prompty.colours._getColourCode("145",prompty.colours.BACKGROUND) )

    def test_getColourCode24Bit(self):
        self.assertEquals("38;2;0;0;0", prompty.colours._getColourCode("#000000") )
        self.assertEquals("38;2;1;2;3", prompty.colours._getColourCode("#010203") )
        self.assertEquals("38;2;255;255;255", prompty.colours._getColourCode("#ffffff") )
        self.assertEquals("38;2;0;0;0", prompty.colours._getColourCode("0,0,0") )
        self.assertEquals("38;2;1;2;3", prompty.colours._getColourCode("1,2,3") )
        self.assertEquals("38;2;255;255;255", prompty.colours._getColourCode("255,255,255") )
        self.assertRaises(ValueError, prompty.colours._getColourCode, "0,0")

    def test_getColourCodeBg24Bit(self):
        self.assertEquals("48;2;1;2;3", prompty.colours._getColourCode("#010203",prompty.colours.BACKGROUND) )
        self.assertEquals("48;2;1;2;3", prompty.colours._getColourCode("1,2,3",prompty.colours.BACKGROUND) )

    def test_getStyleCode(self):
        self.assertIs(prompty.colours._getStyleCode(prompty.colours.NORMAL), prompty.colours.NORMAL[prompty.colours.VAL_KEY])
        self.assertIs(prompty.colours._getStyleCode("italic"), prompty.colours.ITALIC[prompty.colours.VAL_KEY])
        self.assertIs(prompty.colours._getStyleCode("b"), prompty.colours.BOLD[prompty.colours.VAL_KEY])
        for style in prompty.colours.STYLES:
            self.assertEquals(prompty.colours._getStyleCode(style), style[prompty.colours.VAL_KEY])
            self.assertEquals(prompty.colours._getStyleCode(style[prompty.colours.NAME_KEY]), style[prompty.colours.VAL_KEY])
            self.assertEquals(prompty.colours._getStyleCode(style[prompty.colours.CODE_KEY]), style[prompty.colours.VAL_KEY])
        self.assertRaises(KeyError, prompty.colours._getStyleCode, "upsidedown")
 
    def test_stopColour(self):
        self.assertEqual(prompty.colours.stopColour(None), "\001\033[0m\002")
        self.assertEqual(prompty.colours.stopColour(None, False), "\033[0m")
 
    def test_startColour(self):
        self.assertEqual(prompty.colours.startColour(None, "green"), "\001\033[32m\002")
        self.assertEqual(prompty.colours.startColour(None, "green", wrap=False), "\033[32m")
        self.assertEqual(prompty.colours.startColour(None, "red",style="b"), "\001\033[1;31m\002")
        self.assertEqual(prompty.colours.startColour(None, "1"), "\001\033[38;5;1m\002")
        self.assertEqual(prompty.colours.startColour(None, fgcolour="1", bgcolour="2"), "\001\033[38;5;1;48;5;2m\002")
 
    def test_dynamicColourWrappers(self):
        prompty.colours._populateFunctions(sys.modules[__name__])
        self.assertEqual(sys.modules[__name__].green(None, "I'm green"), "\001\033[32m\002I'm green\001\033[0m\002")
        self.assertEqual(sys.modules[__name__].green(None, "I'm green and bold", "bold"), "\001\033[1;32m\002I'm green and bold\001\033[0m\002")


class PaletteTests(UnitTestWrapper):
    def test_defaultPalette(self):
        self.assertEqual(prompty.colours.startColour(None, "pal_c1"), "\001\033[97m\002")
        self.assertEqual(prompty.colours.startColour(None, "pal_a2"), "\001\033[33m\002")
        self.assertEqual(prompty.colours.startColour(None, "pal_a3"), "\001\033[32m\002")
    
    def test_editPalette(self):
        prompty.colours._setPalette("pal_a1", prompty.colours.RED)
        self.assertEqual(prompty.colours.startColour(None, "pal_a1"), "\001\033[31m\002")
        prompty.colours._setPalette("pal_a1", "123")
        self.assertEqual(prompty.colours.startColour(None, "pal_a1"), "\001\033[38;5;123m\002")
        prompty.colours._setPalette("mypal", prompty.colours.GREEN)
        self.assertEqual(prompty.colours.startColour(None, "mypal"), "\001\033[32m\002")


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

class CoordsTests(UnitTestWrapper):
    def test_init(self):
        c = prompty.status.Coords()
        self.assertEqual(0, c.column)
        self.assertEqual(0, c.row)
        c = prompty.status.Coords(5,4)
        self.assertEqual(5, c.column)
        self.assertEqual(4, c.row)
        
    def test_add(self):
        c1 = prompty.status.Coords(1,2)
        c2 = prompty.status.Coords(3,4)
        c3 = c1 + c2
        self.assertEqual(1, c1.column)
        self.assertEqual(2, c1.row)
        self.assertEqual(3, c2.column)
        self.assertEqual(4, c2.row)
        self.assertEqual(4, c3.column)
        self.assertEqual(6, c3.row)

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
        c = prompty.compiler.Compiler(funcs)
        c.compile(r"a b\newline")
        c.execute()
        self.assertEqual(0, funcs.status.pos.column )
        self.assertEqual(1, funcs.status.pos.row )

    def test_singleLiteral(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"literalvalue", c._execute([{'type': 'literal', 'value': r"literalvalue"}]) )

    def test_multipleLiteral(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"literalvalue", c._execute([{'type': 'literal', 'value': r"literal"},
                                                      {'type': 'literal', 'value': r"value"}]) )

    def test_singleFunction(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(CompilerTests.user, c._execute([{'type': 'function', 'name': r"user"}]) )

    def test_nestedFunction(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                     [[{'type': 'function', 'name': r"user"}]]}]) )

    def test_functionWithMultipleLiteralArgument(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[32m\002a%sb%s\001\033[0m\002" % (CompilerTests.user,CompilerTests.host),
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'literal', 'value': r"a"},
                                 {'type': 'function', 'name': r"user"},
                                 {'type': 'literal', 'value': r"b"},
                                 {'type': 'function', 'name': r"hostnamefull"}]]
                          }]) )

    def test_nestedFunctionOptionalArg(self):
        c = prompty.compiler.Compiler()
        self.assertEqual("\001\033[1;32m\002%s\001\033[0m\002" % CompilerTests.user, 
                         c._execute([{'type': 'function', 'name': r"green", 'args': 
                                [[{'type': 'function', 'name': r"user"}]],
                                'optargs': [[{'type': 'literal', 'value': r"bold"}]]
                          }]) )


    def test_multipleAruments(self):
        c = prompty.compiler.Compiler()
        self.assertEqual(r"2", c._execute([{'type': 'function', 'name': r"greater", 'args': 
                                           [[{'type': 'literal', 'value': r"1"}],
                                            [{'type': 'literal', 'value': r"2"}]
                                            ]}]) )

    def test_emptyAruments(self):
        c = prompty.compiler.Compiler()
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
        c = prompty.compiler.Compiler()
        self.assertEqual("True", c._execute([{'args': [[{'type': 'literal', 'value': '1'}], 
                                                    [{'type': 'literal', 'value': '1'}]], 
                                           'type': 'function', 'name': 'equals'}]) )

def testFunc(status):
    return "This Is A Test"

def _hiddenFunc(status):
    return "This is secret"

class FunctionContainerTests(UnitTestWrapper):
    def test_noname(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertRaises(TypeError, c._call)
        
    def test_extendFunctionContainer(self):
        c = prompty.functionContainer.FunctionContainer()
        # Import this module
        c.addFunctions(sys.modules[__name__])
        self.assertEqual(r"This Is A Test", c._call(["testFunc"]))
        self.assertRaises(KeyError, c._call, ["_hiddenFunc"])
        
    def test_extendFunctionContainerFromDir(self):
        c = prompty.functionContainer.FunctionContainer()
        # Import this directory
        c.addFunctionsFromDir(os.path.dirname(sys.modules[__name__].__file__))
        self.assertEqual(r"This Is A Test", c._call(["testFunc"]))

class StandardFunctionTests(UnitTestWrapper):

    def test_user(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(getpass.getuser(), c._call(["user"]))

    def test_hostname(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(socket.gethostname().split(".")[0], c._call(["hostname"]))

    def test_hostnamefull(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(socket.gethostname(), c._call(["hostnamefull"]))

    def test_workingdir(self):
        origcwd = os.getcwd()
        c = prompty.functionContainer.FunctionContainer()
        os.chdir(os.path.expanduser("~"))
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(r"~", c._call(["workingdir"]))
        tmpDir = tempfile.mkdtemp()
        os.chdir(tmpDir)
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(tmpDir, c._call(["workingdir"]))
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
        self.assertEqual(os.path.basename(tmpDir), c._call(["workingdirbase"]))
        os.chdir("/usr/local")
        os.environ["PWD"] = os.getcwd()
        self.assertEqual(r"local", c._call(["workingdirbase"]))
        # Cleanup
        os.chdir(origcwd)
        os.environ["PWD"] = os.getcwd()
        shutil.rmtree(tmpDir)

    def test_dollar(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(r"$", c._call(["dollar"]))
        self.assertEqual(r"#", c._call(["dollar"],0))

    def test_specialChars(self):
        c = prompty.functionContainer.FunctionContainer()
        chars = [
                 ("newline",            "\n"),
                 ("carriagereturn",     "\r"),
                 ("space",              " "),
                 ("backslash",          "\\"),
                 ("percent",            "%"),
                 ("opencurly",          "{"),
                 ("closecurly",         "}"),
                 ("opensquare",         "["),
                 ("closesquare",        "]"),
                 ("escape",             "\033")
                ]
        for char in chars:
            self.assertEqual(char[1], c._call([char[0]]))

    def test_date(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(bool(re.match(r"^[a-zA-z]+ [a-zA-z]+ [0-9]+$",c._call(["date"]))))

    def test_datefmt(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(bool(re.match(r"^[0-9:]+$",c._call(["datefmt"]))))
        self.assertTrue(bool(re.match(r"^hello$",c._call(["datefmt"],"hello"))))
        self.assertTrue(bool(re.match(r"^[0-9]{2}$",c._call(["datefmt"],"#d"))))

    def test_isRealPath(self):
        origcwd = os.getcwd()
        c = prompty.functionContainer.FunctionContainer()
        self.assertTrue(c._call(["isrealpath"]))
        tmpDir = tempfile.mkdtemp()
        link = os.path.join(tmpDir, "link")
        os.symlink(tmpDir, link)
        os.chdir(link)
        os.environ["PWD"] = link
        self.assertFalse(c._call(["isrealpath"]))
        # Cleanup
        os.chdir(origcwd)
        os.environ["PWD"] = os.getcwd()
        shutil.rmtree(tmpDir)


class ExpressionFunctionTests(UnitTestWrapper):
    def test_equal(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual(True, c._call(["equals"],"1","1"))

    def test_if(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual("1", c._call(["ifexpr"],"True","1","2"))
        self.assertEqual("2", c._call(["ifexpr"],"False","1","2"))
        self.assertEqual("1", c._call(["ifexpr"],"True","1"))
        self.assertEqual("", c._call(["ifexpr"],"0","1"))
        self.assertEqual("1", c._call(["ifexpr"],"1","1"))

    def test_exitSuccess(self):
        c = prompty.functionContainer.FunctionContainer(prompty.status.Status(0))
        self.assertEqual(True, c._call(["exitsuccess"]))
        c = prompty.functionContainer.FunctionContainer(prompty.status.Status(1))
        self.assertEqual(False, c._call(["exitsuccess"]))


class ColourFunctionTests(UnitTestWrapper):
    def test_colourLiteral(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertEqual("\001\033[32m\002I'm green\001\033[0m\002",  c._call(["green"],"I'm green"))
        self.assertEqual("\001\033[31m\002I'm red\001\033[0m\002",    c._call(["red"],"I'm red"))


class PromptTests(UnitTestWrapper):
    def test_create(self):
        p = prompty.prompty.Prompt(prompty.status.Status())
        self.assertIsInstance(p, prompty.prompty.Prompt)
 
    def test_getPrompt(self):
        p = prompty.prompty.Prompt(prompty.status.Status())
        s = p.getPrompt()
        self.assertIsInstance(s, basestring)
        self.assertGreater(len(s), 0)


class UserDirTests(UnitTestWrapper):
    def test_userDirLocation(self):
        u = prompty.userdir.UserDir()
        self.assertEquals(os.path.join(os.path.expanduser('~'),prompty.userdir.PROMPTY_USER_DIR), u.getDir())

    def test_functionsDirLocation(self):
        u = prompty.userdir.UserDir()
        self.assertEquals(os.path.join(os.path.expanduser('~'),prompty.userdir.PROMPTY_USER_DIR,prompty.userdir.FUNCTIONS_DIR), u.promtyUserFunctionsDir)

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


class ConfigTests(UnitTestWrapper):
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


class GitTests(UnitTestWrapper):
    def test_commandAvailable(self):
        git_installed = bool(distutils.spawn.find_executable(prompty.git.GIT_COMMAND))
        g = prompty.git.Git()
        self.assertEquals(git_installed, g.installed)
        g = prompty.git.Git("bogus_command_foo")
        self.assertEquals(False, g.installed)

class SvnTests(UnitTestWrapper):
    def test_commandAvailable(self):
        svn_installed = bool(distutils.spawn.find_executable(prompty.svn.SVN_COMMAND))
        s = prompty.svn.Subversion()
        self.assertEquals(svn_installed, s.installed)
        s = prompty.svn.Subversion("bogus_command_foo")
        self.assertEquals(False, s.installed)



#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    print "Prompty module path: %s" % prompty.__path__[0]
    sys.exit(unittest.main())
