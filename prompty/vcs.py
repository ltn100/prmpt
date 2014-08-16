#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import abc
import subprocess



class VCS(object):
    """
    A container class for Version Control System
    sub classes.
    """
    def __init__(self):
        self.vcsObjs = []
        self.ranStatus = False
        self.cwd = None
        self.currentVcsObj = None
        self.populateVCS()

    def populateVCS(self):
        # The order here defines the order in which repository
        # types are tested. The first one found to be a valid repo
        # will halt all further searching, so put them in priority
        # order.
        import git
        self.vcsObjs.append(git.Git())

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _runStatus() is also called
        again if the working directory has changed.
        """
        if name in ["populateVCS", "vcsObjs", "ranStatus", "cwd", "currentVcsObj"]:
            return object.__getattribute__(self, name)
        
        if not  self.ranStatus or self.cwd != os.getcwd():
            self.cwd = os.getcwd()
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
    def __init__(self, cmd):
        self.ranStatus = False
        self.command = cmd
        self.cwd = None
        self.branch = ""
        self.remoteBranch = ""
        self.staged = ""
        self.changed = ""
        self.untracked = ""
        self.unmerged = ""
        self.ahead = ""
        self.behind = ""
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
        if not  object.__getattribute__(self, "ranStatus") or \
                object.__getattribute__(self, "cwd") != os.getcwd():
            self.cwd = os.getcwd()
            self.ranStatus = True
            self._runStatus()
        return object.__getattribute__(self, name)

    @staticmethod
    def runCommand(cmdList):
        # Raises OSError if command doesn't exist
        proc = subprocess.Popen(cmdList,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=os.getcwd())
        stdout, stderr = proc.communicate()
        return stdout, stderr, proc.returncode



#--------------------------
# Prompty functions
#--------------------------
def isrepo(status):
    return status.vcs.isRepo

def repobranch(status):
    return status.vcs.branch