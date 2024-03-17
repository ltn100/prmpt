#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import chr

import sys
import os
import re
import socket
import tempfile
import shutil
import getpass
import mock

from test import prmpt
from test import MockProc
from test import UnitTestWrapper


class StandardFunctionTests(UnitTestWrapper):

    def test_user(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(getpass.getuser(), c._call("user"))

    def test_hostname(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(socket.gethostname().split(".")[0], c._call("hostname"))

    def test_hostnamefull(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(socket.gethostname(), c._call("hostnamefull"))

    def test_workingdir(self):
        origcwd = os.getcwd()
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
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
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
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
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(r"$", c._call("dollar"))
        self.assertEqual(r"#", c._call("dollar", 0))

    def test_specialChars(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
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
            self.assertEqual(char[1], c._call(char[0]))

    def test_uniChar(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual('a', c._call("unichar", "97"))
        self.assertEqual('b', c._call("unichar", "0x62"))
        self.assertEqual('c', c._call("unichar", "0o143"))

    def test_lower(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual('lower', c._call("lower", "lower"))
        self.assertEqual('mixed', c._call("lower", "MiXEd"))
        self.assertEqual('all_upper with spaces', c._call("lower", "ALL_UPPER WITH SPACES"))

    def test_join(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual('one:fish', c._call("join", ":", "one", "fish"))
        self.assertEqual('one/fish/cheese', c._call("join", "/", "one", "fish", "cheese"))
        self.assertEqual('', c._call("join", "/"))
        self.assertRaises(TypeError, c._call, "join")

    @mock.patch('prmpt.status.subprocess')
    def test_justify(self, mock_sp):
        # Set up mock
        output = (
            "54 13",
            "",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual('|     |     |', c._call("justify", "|", "|", "|"))
        self.assertEqual('|-----|=====|', c._call("justify", "|", "|", "|", "-", "="))
        self.assertEqual('            |', c._call("right", "|"))
        self.assertEqual('lt@@@cen   rt', c._call("justify", "lt", "cen", "rt", "@"))

    def test_smiley(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        c.addFunctionsFromModule(prmpt.colours)
        c.status.exitCode = 0
        self.assertIn(":)", c._call("smiley"))
        c.status.exitCode = 1
        self.assertIn(":(", c._call("smiley"))

    def test_powerline(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        c.addFunctionsFromModule(prmpt.colours)
        self.assertIn("test", c._call("powerline", "test"))
        self.assertIn(chr(0xe0b0), c._call("powerline", "test"))

    def test_date(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertTrue(bool(re.match(r"^[a-zA-z]+ [a-zA-z]+ [0-9]+$", c._call("date"))))

    def test_datefmt(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertTrue(bool(re.match(r"^[0-9:]+$", c._call("datefmt"))))
        self.assertTrue(bool(re.match(r"^hello$", c._call("datefmt", "hello"))))
        self.assertTrue(bool(re.match(r"^[0-9]{2}$", c._call("datefmt", "#d"))))

    def test_isRealPath(self):
        origcwd = os.getcwd()
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
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


class ExpressionFunctionTests(UnitTestWrapper):
    def test_equal(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(True, c._call("equals", "1", "1"))

    def test_max(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual("2", c._call("max", "2", "1"))
        self.assertEqual("1", c._call("max", "1", "1"))
        self.assertEqual("2", c._call("max", "1", "2"))

    def test_if(self):
        c = prmpt.functionContainer.FunctionContainer()
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual("1", c._call("ifexpr", "True", "1", "2"))
        self.assertEqual("2", c._call("ifexpr", "False", "1", "2"))
        self.assertEqual("1", c._call("ifexpr", "True", "1"))
        self.assertEqual("", c._call("ifexpr", "0", "1"))
        self.assertEqual("1", c._call("ifexpr", "1", "1"))

    def test_exitSuccess(self):
        c = prmpt.functionContainer.FunctionContainer(prmpt.status.Status(0))
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(True, c._call("exitsuccess"))
        c = prmpt.functionContainer.FunctionContainer(prmpt.status.Status(1))
        c.addFunctionsFromModule(prmpt.functions)
        self.assertEqual(False, c._call("exitsuccess"))
