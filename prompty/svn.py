#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import vcs
import re
import xml.dom.minidom

SVN_COMMAND="svn"


class Subversion(vcs.VCSBase):
    def __init__(self, status, cmd=SVN_COMMAND):
        super(Subversion, self).__init__(status, cmd)

    def _runStatus(self):
        try:
            (stdout, stderr, returncode) = self.runCommand(
                [self.command, "info", "--xml"]
            )
        except OSError:
            # SVN command not found
            self.installed = False
            self.isRepo = False
            return

        if not stderr:
            info = xml.dom.minidom.parseString(stdout)
            entry = info.documentElement.getElementsByTagName("entry")[0]
            # Successful svn status call
            self.installed = True
            self.isRepo = True
            branch = entry.getElementsByTagName("relative-url")[0].childNodes[0].data
            b = re.search('[\^]?/([^/]*)/?([^/]*)?', branch)
            if b:
                self.branch = b.group(1)
                if self.branch in ["branches", "tags"]:
                    self.branch += "/" + b.group(2)
                    
            self.remotebranch = self.branch
            (self.staged,
            self.changed,
            self.untracked,
            self.unmerged,
            self.ahead,
            self.behind) = self._svn_status()
        else:
            if "is not a working copy" in stderr:
                # The directory is not a svn repo
                self.installed = True
                self.isRepo = False
            else:
                # Some other error?
                self.installed = False
                self.isRepo = False


    def _svn_status(self):
        return (0,0,0,0,0,0)
