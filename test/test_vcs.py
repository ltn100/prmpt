#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import socket
import getpass
import distutils
import mock

from test_prompty import UnitTestWrapper
from test_prompty import prompty


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


class GitTests(UnitTestWrapper):

    def test_init(self):
        g = prompty.git.Git(prompty.status.Status(0))
        self.assertIsInstance(g, prompty.vcs.VCSBase)
        self.assertEquals(g.command, prompty.git.GIT_COMMAND)

    @mock.patch('prompty.vcs.subprocess')
    def test_gitUnavailable(self, mock_sp):
        # Set up mock
        output = (
            "",
            "git: command not found",
            127,
            OSError
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.git.Git(prompty.status.Status(0))
        self.assertEquals(False, g.installed)
        self.assertEquals(False, g.isRepo)
        self.assertEquals("", g.branch)
        self.assertEquals(0, g.changed)
        self.assertEquals(0, g.staged)
        self.assertEquals(0, g.unmerged)
        self.assertEquals(0, g.untracked)

    @mock.patch('prompty.vcs.subprocess')
    def test_cleanRepo(self, mock_sp):
        # Set up mock
        output = (
            "## develop...origin/develop\n",
            "",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.git.Git(prompty.status.Status(0))
        self.assertEquals(True, g.installed)
        self.assertEquals(True, g.isRepo)
        self.assertEquals("develop", g.branch)
        self.assertEquals(0, g.changed)
        self.assertEquals(0, g.staged)
        self.assertEquals(0, g.unmerged)
        self.assertEquals(0, g.untracked)

    @mock.patch('prompty.vcs.subprocess')
    def test_dirtyRepo(self, mock_sp):
        # Set up mock
        output = (
            "## master...origin/master\n" +
            "M  bin/prompty\n" +
            " M prompty/prompt.py\n" +
            "A  test/test_prompty.py\n" +
            "AU test.py\n" +
            "?? test/test_git.py",
            "",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.git.Git(prompty.status.Status(0))
        self.assertEquals(True, g.installed)
        self.assertEquals(True, g.isRepo)
        self.assertEquals("master", g.branch)
        self.assertEquals(1, g.changed)
        self.assertEquals(2, g.staged)
        self.assertEquals(1, g.unmerged)
        self.assertEquals(1, g.untracked)

    @mock.patch('prompty.vcs.subprocess')
    def test_notARepo(self, mock_sp):
        # Set up mock
        output = (
            "",
            "fatal: Not a git repository (or any of the parent directories): .git\n",
            128,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.git.Git(prompty.status.Status(0))
        self.assertEquals(True, g.installed)
        self.assertEquals(False, g.isRepo)
        self.assertEquals("", g.branch)
        self.assertEquals(0, g.changed)
        self.assertEquals(0, g.staged)
        self.assertEquals(0, g.unmerged)
        self.assertEquals(0, g.untracked)


class SvnTests(UnitTestWrapper):
    def test_init(self):
        g = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertIsInstance(g, prompty.vcs.VCSBase)
        self.assertEquals(g.command, prompty.svn.SVN_COMMAND)

    def test_commandAvailable(self):
        svn_installed = bool(distutils.spawn.find_executable(prompty.svn.SVN_COMMAND))
        s = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertEquals(svn_installed, s.installed)
        s = prompty.svn.Subversion(prompty.status.Status(0), "bogus_command_foo")
        self.assertEquals(False, s.installed)


