#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str

# Import external modules
import sys
import os
import re
import socket
import shutil
import tempfile
import unittest
import distutils.spawn
from contextlib import contextmanager
from io import StringIO

from test import prmpt, prmpt_bin, TEST_DIR
from test import UnitTestWrapper

_MAX_LENGTH = 80


def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'


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
        argv = ["", "-h"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertEqual(out.getvalue(), "")
        self.assertGreater(len(err.getvalue()), 0)
        self.assertEqual(ret, 0)

    def test_bash(self):
        argv = ["", "-b"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertTrue(out.getvalue().startswith("export PS1"))
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

    def test_prmpt(self):
        argv = ["", "1"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertGreater(len(out.getvalue()), 0)
        self.assertEqual(len(err.getvalue()), 0)
        self.assertEqual(ret, 1)

    def test_invalid(self):
        argv = ["", "-@"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertEqual(out.getvalue(), "")
        self.assertGreater(len(err.getvalue()), 0)
        self.assertEqual(ret, 1)

    def test_colours(self):
        argv = ["", "-c"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertGreater(len(out.getvalue().splitlines()), 1)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)

    def test_pallete(self):
        argv = ["", "-p"]
        with captured_output() as (out, err):
            ret = prmpt_bin.main(argv)

        self.assertGreater(len(out.getvalue().splitlines()), 1)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(ret, 0)


class CoordsTests(UnitTestWrapper):
    def test_init(self):
        c = prmpt.status.Coords()
        self.assertEqual(0, c.column)
        self.assertEqual(0, c.row)
        c = prmpt.status.Coords(5, 4)
        self.assertEqual(5, c.column)
        self.assertEqual(4, c.row)

    def test_add(self):
        c1 = prmpt.status.Coords(1, 2)
        c2 = prmpt.status.Coords(3, 4)
        c3 = c1 + c2
        self.assertEqual(1, c1.column)
        self.assertEqual(2, c1.row)
        self.assertEqual(3, c2.column)
        self.assertEqual(4, c2.row)
        self.assertEqual(4, c3.column)
        self.assertEqual(6, c3.row)


class PromptTests(UnitTestWrapper):
    def test_create(self):
        p = prmpt.prompt.Prompt(prmpt.status.Status())
        self.assertIsInstance(p, prmpt.prompt.Prompt)

    def test_getPrompt(self):
        p = prmpt.prompt.Prompt(prmpt.status.Status())
        s = p.getPrompt()
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 0)


class UserDirTests(UnitTestWrapper):
    def test_userDirLocation(self):
        u = prmpt.userdir.UserDir()
        self.assertEqual(
            os.path.join(os.path.expanduser('~'), prmpt.userdir.PROMPTY_USER_DIR),
            u.getDir()
        )

    def test_functionsDirLocation(self):
        u = prmpt.userdir.UserDir()
        self.assertEqual(
            os.path.join(os.path.expanduser('~'), prmpt.userdir.PROMPTY_USER_DIR, prmpt.userdir.FUNCTIONS_DIR),
            u.promtyUserFunctionsDir
        )

    def test_initialise(self):
        tmpDir = tempfile.mkdtemp()
        u = prmpt.userdir.UserDir(tmpDir)
        self.assertTrue(os.path.isdir(u.getDir()))
        self.assertTrue(os.path.exists(u.getConfigFile()))
        # Cleanup
        shutil.rmtree(tmpDir)

    def test_initialiseExitst(self):
        tmpDir = tempfile.mkdtemp()
        os.makedirs(os.path.dirname(os.path.join(tmpDir, prmpt.userdir.PROMPTY_USER_DIR)))
        # Create .prmpt file in the way
        open(os.path.join(tmpDir, prmpt.userdir.PROMPTY_USER_DIR), 'a').close()
        self.assertRaises(IOError, prmpt.userdir.UserDir, tmpDir)
        # Cleanup
        shutil.rmtree(tmpDir)

    def test_copyFiles(self):
        tmpDir = tempfile.mkdtemp()
        test1 = os.path.join(tmpDir, "test1")
        test2 = os.path.join(tmpDir, "test2")
        # touch test1
        open(os.path.join(tmpDir, "test1"), 'a').close()
        prmpt.userdir.UserDir.copy(test1, test2)
        self.assertTrue(os.path.exists(test2))
        self.assertRaises(IOError, prmpt.userdir.UserDir.copy, "/file/doesnt/exist", test2)
        # Cleanup
        shutil.rmtree(tmpDir)


class ConfigTests(UnitTestWrapper):
    def test_loadConfig(self):
        c = prmpt.config.Config()
        c.load(os.path.join(os.path.dirname(TEST_DIR),
                            prmpt.userdir.SKEL_DIR,
                            prmpt.userdir.PROMPTY_CONFIG_FILE))
        self.assertEqual(
            os.path.join(os.path.dirname(TEST_DIR), prmpt.userdir.SKEL_DIR, "default.prmpt"),
            c.promptFile
        )

    def test_loadPrompt(self):
        c = prmpt.config.Config()
        c.promptFile = os.path.join(os.path.dirname(TEST_DIR), prmpt.userdir.SKEL_DIR, "default.prmpt")
        c.loadPromptFile()
        self.assertGreater(len(c.promptString), 0)
