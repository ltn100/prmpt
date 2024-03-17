#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
ABC = abc.ABCMeta(str('ABC'), (object,), {'__slots__': ()})  # noqa, compatible with Python 2 *and* 3

from builtins import str
import subprocess

from prmpt import functionBase


class VCS(object):
    """
    A container class for Version Control System
    sub classes.
    """
    def __init__(self, status):
        self.status = status
        self.vcsObjs = []
        self.ranStatus = False
        self.cwd = None
        self.populateVCS()
        self.currentVcsObj = self.vcsObjs[0]

    def populateVCS(self):
        # The order here defines the order in which repository
        # types are tested. The first one found to be a valid repo
        # will halt all further searching, so put them in priority
        # order.
        from . import git
        self.vcsObjs.append(git.Git(self.status))
        from . import svn
        self.vcsObjs.append(svn.Subversion(self.status))

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _runStatus() is also called
        again if the working directory has changed.
        """
        if name in ["populateVCS", "vcsObjs", "ranStatus", "cwd", "currentVcsObj", "status"]:
            return object.__getattribute__(self, name)

        if not self.ranStatus or self.cwd != self.status.getWorkingDir():
            self.cwd = self.status.getWorkingDir()
            self.ranStatus = True
            for vcs in self.vcsObjs:
                if vcs.isRepo:
                    self.currentVcsObj = vcs
                    break

        return getattr(object.__getattribute__(self, "currentVcsObj"), name)


class VCSBase(ABC):
    """
    An abstract base class for VCS sub classes
    """

    @abc.abstractmethod
    def __init__(self, status, cmd):
        self.status = status
        self.ranStatus = False
        self.command = cmd
        self.cwd = None
        self.branch = ""
        self.remoteBranch = ""
        self.staged = 0
        self.changed = 0
        self.untracked = 0
        self.unmerged = 0
        self.ahead = 0
        self.behind = 0
        self.installed = None
        self.isRepo = None
        self.commit = ""
        self.last_fetched = 0
        self.relative_root = ""

    @abc.abstractmethod
    def _runStatus(self):
        """
        Method is abstract and must be implemented. This method
        sets appropriately all of the member variables defined
        in __init__()
        """
        pass

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _runStatus() is also called
        again if the working directory has changed.
        """
        if name in ["ranStatus", "cwd", "status"]:
            return object.__getattribute__(self, name)

        if not self.ranStatus or self.cwd != self.status.getWorkingDir():
            self.cwd = self.status.getWorkingDir()
            self.ranStatus = True
            self._runStatus()
        return object.__getattribute__(self, name)

    def runCommand(self, cmdList):
        # Raises OSError if command doesn't exist
        proc = subprocess.Popen(cmdList,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=self.status.getWorkingDir())
        stdout, stderr = proc.communicate()
        return stdout.decode('utf-8'), stderr.decode('utf-8'), proc.returncode


# --------------------------
# Prmpt functions
# --------------------------
class VCSFunctions(functionBase.PrmptFunctions):

    def isrepo(self):
        """
        Return ``True`` if the current working directory is a version control repository.

        :rtype: bool
        """
        return self.status.vcs.isRepo

    def repobranch(self):
        """
        The repository branch name.
        """
        return self.status.vcs.branch

    def isrepodirty(self):
        """
        Return ``True`` if the repository has uncommited modifications.

        :rtype: bool
        """
        if self.status.vcs.changed + self.status.vcs.staged + self.status.vcs.unmerged > 0:
            return True
        else:
            return False

    def ahead(self):
        """
        Get the number of commits ahead of the remote repository.
        """
        return self.status.vcs.ahead

    def behind(self):
        """
        Get the number of commits behind the remote repository.
        """
        return self.status.vcs.behind

    def commit(self):
        return self.status.vcs.commit

    def staged(self):
        """
        Get the number of files that are currently staged.
        """
        return self.status.vcs.staged

    def changed(self):
        """
        Get the number of files that are modified and not staged.
        """
        return self.status.vcs.changed

    def untracked(self):
        """
        Get the number of untracked files that are in the repository (excluding those ignored).
        """
        return self.status.vcs.untracked

    def last_fetched(self):
        """
        Get the time, in seconds, since the remote was last fetched.
        """
        return self.status.vcs.last_fetched

    def last_fetched_min(self):
        """
        Get the time, in minutes, since the remote was last fetched.
        """
        return self.status.vcs.last_fetched // 60
