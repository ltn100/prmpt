#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
import os
import sys
import imp
import unittest

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
    print(__file__)
    print(os.path.dirname(TEST_DIR))
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


class UnitTestWrapper(unittest.TestCase):
    """
    A wrapper for the unittest class to enable support
    for functions not available in python 2.6
    """
    pass


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
                raise self.failureException(
                    'First sequence is not a %s: %s'
                    % (seq_type_name, safe_repr(seq1))
                )
            if not isinstance(seq2, seq_type):
                raise self.failureException(
                    'Second sequence is not a %s: %s'
                    % (seq_type_name, safe_repr(seq2))
                )
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

            for i in range(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' % (i, seq_type_name))
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' % (i, seq_type_name))
                    break

                if item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' % (i, item1, item2))
                    break
            else:
                if (len1 == len2 and seq_type is None and type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += ('\nFirst %s contains %d additional elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' % (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing += ('\nSecond %s contains %d additional elements.\n' % (seq_type_name, len2 - len1))
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
