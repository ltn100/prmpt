#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import shutil
import errno
import distutils.dir_util


PROMPTY_USER_DIR = os.path.join(".local", "share", "prompty")
PROMPTY_CONFIG_FILE = "prompty.cfg"
SKEL_DIR = "skel"
FUNCTIONS_DIR = "functions"


def getPromptyBaseDir():
    """
    Get the directory where the prompty module is located
    """
    return os.path.dirname(
        os.path.dirname(
            # The filename of this module
            os.path.normpath(os.path.abspath(sys.modules[__name__].__file__))
        )
    )


class UserDir(object):
    def __init__(self, homeDir=None):
        if homeDir is None:
            self.homeDir = os.path.expanduser('~')
        else:
            self.homeDir = homeDir
        self.promtyUserDir = os.path.join(self.homeDir, PROMPTY_USER_DIR)
        self.promtyBaseDir = getPromptyBaseDir()
        self.promtyUserFunctionsDir = os.path.join(self.promtyUserDir, FUNCTIONS_DIR)

        self.skelDir = os.path.join(self.promtyBaseDir, SKEL_DIR)
        if not os.path.exists(self.skelDir):
            # Installed locally
            self.skelDir = os.path.join(self.homeDir, ".local", "share", "prompty", SKEL_DIR)

            if not os.path.exists(self.skelDir):
                # Install dir as defined in setup.py
                self.skelDir = os.path.join(sys.prefix, "share", "prompty", SKEL_DIR)

                if not os.path.exists(self.skelDir):
                    # Install dir as defined in setup.py
                    self.skelDir = os.path.join(sys.prefix, "local", "share", "prompty", SKEL_DIR)

                if not os.path.exists(self.skelDir):
                    raise IOError("Cannot find installed skel directory")

        # Initialise if promptyUserDir does not exist
        self.initialise()

    def initialise(self):
        if not os.path.isfile(self.getConfigFile()):
            # No prompty dir - check if there is a file blocking the name
            if os.path.isfile(self.promtyUserDir):
                raise IOError("Cannot create %s directory - file exists!" % PROMPTY_USER_DIR)

            # Create prompty dir from skel
            self.copy(self.skelDir, self.promtyUserDir)

    @staticmethod
    def copy(src, dest):
        try:
            if os.path.isdir(src):
                distutils.dir_util.copy_tree(src, dest)
            else:
                shutil.copytree(src, dest)

        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                raise IOError('Directory not copied. Error: %s' % e)

    def getDir(self):
        return self.promtyUserDir

    def getConfigFile(self):
        return os.path.join(self.promtyUserDir, PROMPTY_CONFIG_FILE)
