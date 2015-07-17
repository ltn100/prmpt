#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import abc
import subprocess

import status

import functionBase

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
        import git
        self.vcsObjs.append(git.Git(self.status))
        import svn
        self.vcsObjs.append(svn.Subversion(self.status))

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _runStatus() is also called
        again if the working directory has changed.
        """
        if name in ["populateVCS", "vcsObjs", "ranStatus", "cwd", "currentVcsObj", "status"]:
            return object.__getattribute__(self, name)
        
        if not  self.ranStatus or self.cwd != self.status.getWorkingDir():
            self.cwd = self.status.getWorkingDir()
            self.ranStatus = True
            for vcs in self.vcsObjs:
                if vcs.isRepo:
                    self.currentVcsObj = vcs
                    break

        return getattr(object.__getattribute__(self, "currentVcsObj"), name)



class VCSBase(object):
    """
    An abstract base class for VCS sub classes
    """
    __metaclass__ = abc.ABCMeta
    
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

    def runCommand(self, cmdList, workingDir=None):
        # Raises OSError if command doesn't exist
        proc = subprocess.Popen(cmdList,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=self.status.getWorkingDir())
        stdout, stderr = proc.communicate()
        return stdout, stderr, proc.returncode


# --------------------------
# Prompty functions
# --------------------------
class VCSFunctions(functionBase.PromptyFunctions):

    def isrepo(self):
        return self.status.vcs.isRepo

    def repobranch(self):
        return self.status.vcs.branch

    def isrepodirty(self):
        if self.status.vcs.changed + self.status.vcs.staged + self.status.vcs.unmerged > 0:
            return True
        else:
            return False
