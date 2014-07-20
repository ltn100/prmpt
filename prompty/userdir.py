#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os

PROMPTY_USER_DIR = ".prompty"

class UserDir(object):
    def __init__(self):
        self.homeDir = os.path.expanduser('~')
        self.promtyDir = os.path.join(self.homeDir,PROMPTY_USER_DIR)
    
    def getDir(self):
        return self.promtyDir