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
            "## master...origin/master [ahead 14, behind 58]\n" +
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
        self.assertEquals(14, g.ahead)
        self.assertEquals(58, g.behind)

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

    @mock.patch('prompty.vcs.subprocess')
    def test_svnUnavailable(self, mock_sp):
        # Set up mock
        output = (
            "",
            "svn: command not found",
            127,
            OSError
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertEquals(False, g.installed)
        self.assertEquals(False, g.isRepo)
        self.assertEquals("", g.branch)
        self.assertEquals(0, g.changed)
        self.assertEquals(0, g.untracked)

    @mock.patch('prompty.vcs.subprocess')
    def test_notARepo(self, mock_sp):
        # Set up mock
        output = (
            "",
            "svn: warning: W155007: '/home/user/myrepo' is not a working copy\n",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertEquals(True, g.installed)
        self.assertEquals(False, g.isRepo)
        self.assertEquals("", g.branch)
        self.assertEquals(0, g.changed)
        self.assertEquals(0, g.staged)
        self.assertEquals(0, g.unmerged)
        self.assertEquals(0, g.untracked)

    @mock.patch('prompty.vcs.subprocess')
    def test_info(self, mock_sp):
        # Set up mock
        output = (
            '<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<info>\n' +
            '<entry\n' +
            '   path="."\n' +
            '   revision="5228"\n' +
            '   kind="dir">\n' +
            '<url>https://localhost/repos/myrepo/trunk</url>\n' +
            '<relative-url>^/trunk</relative-url>\n' +
            '<repository>\n'+
            '<root>https://localhost/repos/myrepo</root>\n' +
            '<uuid>1cf8179b-9667-814b-b662-e110218c33db</uuid>\n' +
            '</repository>\n' +
            '<wc-info>\n' +
            '<wcroot-abspath>/home/user/myrepo</wcroot-abspath>\n' +
            '<schedule>normal</schedule>\n' +
            '<depth>infinity</depth>\n' +
            '</wc-info>\n' +
            '<commit\n' +
            '   revision="5228">\n' +
            '<author>ltn100</author>\n' +
            '<date>2015-05-01T21:29:01.683640Z</date>\n' +
            '</commit>\n' +
            '</entry>\n' +
            '</info>\n',
            "",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertEquals(True, g.installed)
        self.assertEquals(True, g.isRepo)
        self.assertEquals("trunk", g.branch)

    @mock.patch('prompty.vcs.subprocess')
    def test_status(self, mock_sp):
        # Set up mock
        output = (
            'M       test/myfile1.txt\n' +
            'A       test/myfile2.txt\n' +
            'C       test/myfile3.txt\n' +
            'D       test/myfile4.txt\n' +
            '!       test/myfile5.txt\n' +
            '?       test/myfile6.txt\n' +
            '?       test/myfile7.txt\n',
            "",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prompty.svn.Subversion(prompty.status.Status(0))
        self.assertEquals(5, g.changed)
        self.assertEquals(2, g.untracked)