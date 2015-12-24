#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import os
import re
import imp
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
    if os.path.isdir("prompty") and os.path.isdir("test") and os.path.isdir("bin"):
        sys.path[0:0] = [os.getcwd()]
        prompty_exec = os.path.join("bin", "prompty")
    else:
        prompty_exec = distutils.spawn.find_executable("prompty")
    
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

class MockProc(object):

    def __init__(self, output):
        (self.stdout, self.stderr, self.returncode, self.exception) = output

    def __getattr__(self, key):
        if key == 'returncode':
            return self.returncode
        else:
            raise AttributeError(key)

    def communicate(self):
        if self.exception:
            raise self.exception
        else:
            return (self.stdout, self.stderr)

if True or "assertIn" not in dir(UnitTestWrapper):
    def _assertIn(self, expr1, expr2, msg=None):
        """Just like self.assertTrue(a is b), but with a nicer default message."""
        if expr1 not in expr2:
            standardMsg = '%s not in %s' % (safe_repr(expr1),
                                             safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))
    setattr(UnitTestWrapper, "assertIn", _assertIn)

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

from test_parser import *
from test_colours import *
from test_functionContainer import *
from test_functions import *
from test_vcs import *



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

    def test_prompty(self):
        argv = ["", "1"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertGreater(len(out.getvalue()), 0)
        self.assertEqual(len(err.getvalue()), 0)
        self.assertEqual(ret, 1)

    def test_invalid(self):
        argv = ["","-@"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertEqual(out.getvalue(), "")
        self.assertGreater(len(err.getvalue()), 0)
        self.assertEqual(ret, 1)

    def test_colours(self):
        argv = ["","-c"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertGreater(out.getvalue().split(":"),1)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

    def test_pallete(self):
        argv = ["","-p"]
        with captured_output() as (out, err):
            ret = prompty_bin.main(argv)

        self.assertGreater(out.getvalue().split("_"),1)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

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


class PromptTests(UnitTestWrapper):
    def test_create(self):
        p = prompty.prompt.Prompt(prompty.status.Status())
        self.assertIsInstance(p, prompty.prompt.Prompt)
 
    def test_getPrompt(self):
        p = prompty.prompt.Prompt(prompty.status.Status())
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






#---------------------------------------------------------------------------#
#                          End of functions                                 #
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    print "Prompty module path: %s" % prompty.__path__[0]
    sys.exit(unittest.main())
