#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
ABC = abc.ABCMeta(str('ABC'), (object,), {'__slots__': ()})  # noqa, compatible with Python 2 *and* 3

import subprocess

from prompty import functionBase


class VCS(object):
    """
    A container class for Version Control System
    sub classes.
    """
    def __init__(self, status):
        self.status = status
        self.vcs_objs = []
        self.ran_status = False
        self.cwd = None
        self.populate_vcs()
        self.current_vcs_obj = self.vcs_objs[0]

    def populate_vcs(self):
        # The order here defines the order in which repository
        # types are tested. The first one found to be a valid repo
        # will halt all further searching, so put them in priority
        # order.
        from . import git
        self.vcs_objs.append(git.Git(self.status))
        from . import svn
        self.vcs_objs.append(svn.Subversion(self.status))

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _run_status() is also called
        again if the working directory has changed.
        """
        if name in ["populate_vcs", "vcs_objs", "ran_status", "cwd", "current_vcs_obj", "status"]:
            return object.__getattribute__(self, name)

        if not self.ran_status or self.cwd != self.status.get_working_dir():
            self.cwd = self.status.get_working_dir()
            self.ran_status = True
            for vcs in self.vcs_objs:
                if vcs.is_repo:
                    self.current_vcs_obj = vcs
                    break

        return getattr(object.__getattribute__(self, "current_vcs_obj"), name)


class VCSBase(ABC):
    """
    An abstract base class for VCS sub classes
    """

    @abc.abstractmethod
    def __init__(self, status, cmd):
        self.status = status
        self.ran_status = False
        self.command = cmd
        self.cwd = None
        self.branch = ""
        self.remote_branch = ""
        self.staged = 0
        self.changed = 0
        self.untracked = 0
        self.unmerged = 0
        self.ahead = 0
        self.behind = 0
        self.installed = None
        self.is_repo = None
        self.commit = ""
        self.last_fetched = 0
        self.relative_root = ""

    @abc.abstractmethod
    def _run_status(self):
        """
        Method is abstract and must be implemented. This method
        sets appropriately all of the member variables defined
        in __init__()
        """
        pass

    def __getattribute__(self, name):
        """
        If we have not yet run a status call then run one before
        attempting to get the attribute. _run_status() is also called
        again if the working directory has changed.
        """
        if name in ["ran_status", "cwd", "status"]:
            return object.__getattribute__(self, name)

        if not self.ran_status or self.cwd != self.status.get_working_dir():
            self.cwd = self.status.get_working_dir()
            self.ran_status = True
            self._run_status()
        return object.__getattribute__(self, name)

    def run_command(self, cmd_list):
        # Raises OSError if command doesn't exist
        proc = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=self.status.get_working_dir())
        stdout, stderr = proc.communicate()
        return stdout.decode('utf-8'), stderr.decode('utf-8'), proc.returncode


# --------------------------
# Prompty functions
# --------------------------
class VCSFunctions(functionBase.PromptyFunctions):

    def isrepo(self):
        """
        Return ``True`` if the current working directory is a version control repository.

        :rtype: bool
        """
        return self.status.vcs.is_repo

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
