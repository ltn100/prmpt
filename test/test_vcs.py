#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import socket
import getpass
import distutils
import mock

from test import prmpt
from test import MockProc
from test import UnitTestWrapper


class GitTests(UnitTestWrapper):
    @mock.patch('prmpt.vcs.subprocess')
    def test_init(self, mock_sp):
        # Set up mock
        status_output = (
            "",
            "git: command not found",
            127,
            OSError
        )
        revparse_output = (
            "",
            "git: command not found",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]

        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertIsInstance(g, prmpt.vcs.VCSBase)
        self.assertEqual(g.command, prmpt.git.GIT_COMMAND)

    @mock.patch('prmpt.vcs.subprocess')
    def test_gitUnavailable(self, mock_sp):
        # Set up mock
        status_output = (
            "",
            "git: command not found",
            127,
            OSError
        )
        revparse_output = (
            "",
            "git: command not found",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]

        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertEqual(False, g.installed)
        self.assertEqual(False, g.isRepo)
        self.assertEqual("", g.branch)
        self.assertEqual(0, g.changed)
        self.assertEqual(0, g.staged)
        self.assertEqual(0, g.unmerged)
        self.assertEqual(0, g.untracked)

    @mock.patch('prmpt.vcs.subprocess')
    def test_cleanRepo(self, mock_sp):
        # Set up mock
        status_output = (
            b"## develop...origin/develop\n",
            b"",
            0,
            None
        )
        revparse_output = (
            b"../\n1234567\n",
            b"",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]

        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertEqual(True, g.installed)
        self.assertEqual(True, g.isRepo)
        self.assertEqual("develop", g.branch)
        self.assertEqual(0, g.changed)
        self.assertEqual(0, g.staged)
        self.assertEqual(0, g.unmerged)
        self.assertEqual(0, g.untracked)
        self.assertEqual("1234567", g.commit)

    @mock.patch('prmpt.vcs.subprocess')
    def test_dirtyRepo(self, mock_sp):
        # Set up mock
        status_output = (
            b"## master...origin/master [ahead 14, behind 58]\n" +
            b"M  bin/prmpt\n" +
            b" M prmpt/prompt.py\n" +
            b"A  test/test_prmpt.py\n" +
            b"AU test.py\n" +
            b"?? test/test_git.py",
            b"",
            0,
            None
        )
        revparse_output = (
            b"../\n1234567\n",
            b"",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]

        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertEqual(True, g.installed)
        self.assertEqual(True, g.isRepo)
        self.assertEqual("master", g.branch)
        self.assertEqual(1, g.changed)
        self.assertEqual(2, g.staged)
        self.assertEqual(1, g.unmerged)
        self.assertEqual(1, g.untracked)
        self.assertEqual(14, g.ahead)
        self.assertEqual(58, g.behind)
        self.assertEqual("1234567", g.commit)

    @mock.patch('prmpt.vcs.subprocess')
    def test_notARepo(self, mock_sp):
        # Set up mock
        status_output = (
            b"",
            b"fatal: Not a git repository (or any of the parent directories): .git\n",
            128,
            None
        )
        revparse_output = (
            b"../\n1234567\n",
            b"",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]

        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertEqual(True, g.installed)
        self.assertEqual(False, g.isRepo)
        self.assertEqual("", g.branch)
        self.assertEqual(0, g.changed)
        self.assertEqual(0, g.staged)
        self.assertEqual(0, g.unmerged)
        self.assertEqual(0, g.untracked)
        self.assertEqual("1234567", g.commit)

    @mock.patch('prmpt.vcs.subprocess')
    def test_last_fetched(self, mock_sp):
        # Set up mock
        status_output = (
            b"## develop...origin/develop\n",
            b"",
            0,
            None
        )
        revparse_output = (
            b"../\n1234567\n",
            b"",
            0,
            None
        )
        mock_sp.Popen.side_effect = [MockProc(status_output), MockProc(revparse_output)]
        g = prmpt.git.Git(prmpt.status.Status(0))
        self.assertGreaterEqual(g.last_fetched, 0)
        self.assertEqual('1234567', g.commit)


class SvnTests(UnitTestWrapper):
    def test_init(self):
        g = prmpt.svn.Subversion(prmpt.status.Status(0))
        self.assertIsInstance(g, prmpt.vcs.VCSBase)
        self.assertEqual(g.command, prmpt.svn.SVN_COMMAND)

    @mock.patch('prmpt.vcs.subprocess')
    def test_svnUnavailable(self, mock_sp):
        # Set up mock
        output = (
            b"",
            b"svn: command not found",
            127,
            OSError
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prmpt.svn.Subversion(prmpt.status.Status(0))
        self.assertEqual(False, g.installed)
        self.assertEqual(False, g.isRepo)
        self.assertEqual("", g.branch)
        self.assertEqual(0, g.changed)
        self.assertEqual(0, g.untracked)

    @mock.patch('prmpt.vcs.subprocess')
    def test_notARepo(self, mock_sp):
        # Set up mock
        output = (
            b"",
            b"svn: warning: W155007: '/home/user/myrepo' is not a working copy\n",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prmpt.svn.Subversion(prmpt.status.Status(0))
        self.assertEqual(True, g.installed)
        self.assertEqual(False, g.isRepo)
        self.assertEqual("", g.branch)
        self.assertEqual(0, g.changed)
        self.assertEqual(0, g.staged)
        self.assertEqual(0, g.unmerged)
        self.assertEqual(0, g.untracked)

    @mock.patch('prmpt.vcs.subprocess')
    def test_info(self, mock_sp):
        # Set up mock
        output = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n' +
            b'<info>\n' +
            b'<entry\n' +
            b'   path="."\n' +
            b'   revision="5228"\n' +
            b'   kind="dir">\n' +
            b'<url>https://localhost/repos/myrepo/trunk</url>\n' +
            b'<relative-url>^/trunk</relative-url>\n' +
            b'<repository>\n' +
            b'<root>https://localhost/repos/myrepo</root>\n' +
            b'<uuid>1cf8179b-9667-814b-b662-e110218c33db</uuid>\n' +
            b'</repository>\n' +
            b'<wc-info>\n' +
            b'<wcroot-abspath>/home/user/myrepo</wcroot-abspath>\n' +
            b'<schedule>normal</schedule>\n' +
            b'<depth>infinity</depth>\n' +
            b'</wc-info>\n' +
            b'<commit\n' +
            b'   revision="5228">\n' +
            b'<author>ltn100</author>\n' +
            b'<date>2015-05-01T21:29:01.683640Z</date>\n' +
            b'</commit>\n' +
            b'</entry>\n' +
            b'</info>\n',
            b"",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prmpt.svn.Subversion(prmpt.status.Status(0))
        self.assertEqual(True, g.installed)
        self.assertEqual(True, g.isRepo)
        self.assertEqual("trunk", g.branch)

    @mock.patch('prmpt.vcs.subprocess')
    def test_status(self, mock_sp):
        # Set up mock
        output = (
            b'M       test/myfile1.txt\n' +
            b'A       test/myfile2.txt\n' +
            b'C       test/myfile3.txt\n' +
            b'D       test/myfile4.txt\n' +
            b'!       test/myfile5.txt\n' +
            b'?       test/myfile6.txt\n' +
            b'?       test/myfile7.txt\n',
            b"",
            0,
            None
        )
        mock_sp.Popen.return_value = MockProc(output)

        g = prmpt.svn.Subversion(prmpt.status.Status(0))
        self.assertEqual(5, g.changed)
        self.assertEqual(2, g.untracked)
