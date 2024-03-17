#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import xml.dom.minidom
from xml.parsers.expat import ExpatError

from prmpt import vcs

SVN_COMMAND = "svn"


class Subversion(vcs.VCSBase):

    def __init__(self, status, cmd=SVN_COMMAND):
        super(Subversion, self).__init__(status, cmd)

    def _runStatus(self):
        try:
            (istdout, istderr, _) = self.runCommand(
                [self.command, "info", "--xml"]
            )
            (sstdout, sstderr, _) = self.runCommand(
                [self.command, "status"]
            )
        except OSError:
            # SVN command not found
            self.installed = False
            self.isRepo = False
            return

        if not istderr:
            # Successful svn info call
            self.installed = True
            self._parse_info_xml(istdout)
        else:
            if "is not a working copy" in istderr:
                # The directory is not a svn repo
                self.installed = True
                self.isRepo = False
            else:
                # Some other error?
                self.installed = False
                self.isRepo = False

        if not sstderr:
            # Successful svn status call
            self._parse_status(sstdout)

    def _parse_info_xml(self, xml_string):
        """Parse the return string from a 'svn info --xml' command
        Example string

        <?xml version="1.0" encoding="UTF-8"?>
        <info>
            <entry
               path="/home/my/sandbox" revision="5228" kind="dir">
                <url>https://localhost/repos/myrepo/branches/feature-awesomeFeature</url>
                <relative-url>^/branches/feature-awesomeFeature</relative-url>
                <repository>
                    <root>https://localhost/repos/myrepo</root>
                    <uuid>1cf8279b-9667-814b-b667-e110318c33db</uuid>
                </repository>
                <wc-info>
                    <wcroot-abspath>/home/my/sandbox</wcroot-abspath>
                    <schedule>normal</schedule>
                    <depth>infinity</depth>
                </wc-info>
                <commit revision="5228">
                    <author>me</author>
                    <date>2014-05-01T21:29:01.683640Z</date>
                </commit>
            </entry>
        </info>
        """
        try:
            info = xml.dom.minidom.parseString(xml_string.strip())
        except ExpatError:
            # Error parsing xml
            return

        self.isRepo = True

        entry = info.documentElement.getElementsByTagName("entry")[0]

        branch = entry.getElementsByTagName("relative-url")[0].childNodes[0].data
        b = re.search(r'[\^]?/([^/]*)/?([^/]*)', branch)
        if b:
            self.branch = b.group(1)
            if self.branch in ["branches", "tags"]:
                self.branch += "/" + b.group(2)

        self.remotebranch = self.branch

    def _parse_status(self, status_string):
        """Parse the return string from a 'svn status' command
        """
        for line in status_string.splitlines():
            # First 7 columns in the status lines
            # denote the status
            if len(line) >= 7:
                self._parse_status_line(line[:7])

    def _parse_status_line(self, line):
        """From svn help page:
          ' ' no modifications
          'A' Added
          'C' Conflicted
          'D' Deleted
          'I' Ignored
          'M' Modified
          'R' Replaced
          'X' an unversioned directory created by an externals definition
          '?' item is not under version control
          '!' item is missing (removed by non-svn command) or incomplete
          '~' versioned item obstructed by some item of a different kind
        """
        if line[0] in ('M', 'A', 'D', 'R', 'C', '!', '~'):  # changes in work tree
            self.changed += 1

        if line[0] in ('?', 'I'):  # untracked files
            self.untracked += 1
