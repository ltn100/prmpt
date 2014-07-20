#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import shutil
import errno

import prompty

PROMPTY_USER_DIR = ".prompty"
PROMPTY_CONFIG_FILE = "prompty.cfg"
SKEL_DIR = "skel"

class UserDir(object):
    def __init__(self, homeDir=None):
        if homeDir is None:
            self.homeDir = os.path.expanduser('~')
        else:
            self.homeDir = homeDir
        self.promtyUserDir = os.path.join(self.homeDir,PROMPTY_USER_DIR)
        self.promtyBaseDir = prompty.getPromptyBaseDir()
        self.skelDir = os.path.join(self.promtyBaseDir,SKEL_DIR)
    
    def initialise(self):
        if not os.path.isdir(self.promtyUserDir):
            # No prompty dir - check if there is a file blocking the name
            if os.path.exists(self.promtyUserDir):
                raise IOError("Cannot create %s directory - file exists!" % PROMPTY_USER_DIR)
            
            # Create prompty dir from skel
            self.copy(self.skelDir, self.promtyUserDir)


    @staticmethod
    def copy(src, dest):
        try:
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