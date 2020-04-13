#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import str

# Import external modules
import sys
import os
import re
import socket
import shutil
import tempfile
import unittest
import click.testing
import distutils.spawn
from contextlib import contextmanager
from io import StringIO

from test import prompty, prompty_bin, TEST_DIR
from test import UnitTestWrapper

_MAX_LENGTH = 80


class MainTests(UnitTestWrapper):
    def test_help(self):
        argv = ["--help"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        self.assertGreater(len(result.output), 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 0)

    def test_bash(self):
        argv = ["gen-bashrc"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        self.assertTrue(result.output.startswith("export PS1"))
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 0)

    def test_prompty(self):
        argv = ["-e 1"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        print("********")
        print(result)
        print("********")

        self.assertGreater(len(result.output), 0)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 1)

    def test_invalid(self):
        argv = ["-@"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        self.assertEqual(result.output, "")
        self.assertGreater(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 2)

    def test_colours(self):
        argv = ["colours"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        self.assertGreater(len(result.output.splitlines()), 1)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 0)

    def test_pallete(self):
        argv = ["palette"]
        runner = click.testing.CliRunner(mix_stderr=False)
        result = runner.invoke(prompty_bin.prompty.cli.cli, argv)

        self.assertGreater(len(result.output.splitlines()), 1)
        self.assertEqual(len(result.stderr), 0)
        self.assertEqual(result.exit_code, 0)


class CoordsTests(UnitTestWrapper):
    def test_init(self):
        c = prompty.status.Coords()
        self.assertEqual(0, c.column)
        self.assertEqual(0, c.row)
        c = prompty.status.Coords(5, 4)
        self.assertEqual(5, c.column)
        self.assertEqual(4, c.row)

    def test_add(self):
        c1 = prompty.status.Coords(1, 2)
        c2 = prompty.status.Coords(3, 4)
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
        s = p.get_prompt()
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 0)


class UserDirTests(UnitTestWrapper):
    def test_userDirLocation(self):
        u = prompty.userdir.UserDir()
        self.assertEqual(
            os.path.join(os.path.expanduser('~'), prompty.userdir.PROMPTY_USER_DIR),
            u.get_dir()
        )

    def test_functionsDirLocation(self):
        u = prompty.userdir.UserDir()
        self.assertEqual(
            os.path.join(os.path.expanduser('~'), prompty.userdir.PROMPTY_USER_DIR, prompty.userdir.FUNCTIONS_DIR),
            u.promty_user_functions_dir
        )

    def test_initialise(self):
        tmpDir = tempfile.mkdtemp()
        u = prompty.userdir.UserDir(tmpDir)
        self.assertTrue(os.path.isdir(u.get_dir()))
        self.assertTrue(os.path.exists(u.get_config_file()))
        # Cleanup
        shutil.rmtree(tmpDir)

    def test_initialiseExitst(self):
        tmpDir = tempfile.mkdtemp()
        os.makedirs(os.path.dirname(os.path.join(tmpDir, prompty.userdir.PROMPTY_USER_DIR)))
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
        self.assertEqual(
            os.path.join(os.path.dirname(TEST_DIR), prompty.userdir.SKEL_DIR, "default.prompty"),
            c.prompt_file
        )

    def test_loadPrompt(self):
        c = prompty.config.Config()
        c.prompt_file = os.path.join(os.path.dirname(TEST_DIR), prompty.userdir.SKEL_DIR, "default.prompty")
        c.load_prompt_file()
        self.assertGreater(len(c.prompt_string), 0)
