#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import vcs


SVN_COMMAND="svn"


class Subversion(vcs.VCSBase):
    def __init__(self, cmd=SVN_COMMAND):
        super(Subversion, self).__init__(cmd)

    def _runStatus(self):
        try:
            (stdout, stderr, returncode) = self.runCommand(
                [self.command, "status", "--xml"]
            )
        except OSError:
            # SVN command not found
            self.installed = False
            self.isRepo = False
            return

        if not stderr:
            # Successful svn status call
            self.installed = True
            self.isRepo = True
            (self.branch,
             self.remoteBranch,
             self.staged,
             self.changed,
             self.untracked,
             self.unmerged,
             self.ahead,
             self.behind) = self._svn_status(stdout)
        else:
            if "is not a working copy" in stderr:
                # The directory is not a svn repo
                self.installed = True
                self.isRepo = False
            else:
                # Some other error?
                self.installed = False
                self.isRepo = False


    def _svn_status(self, result):
        pass