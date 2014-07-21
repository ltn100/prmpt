#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import subprocess
from sys import stderr

GIT_COMMAND="git"

class Git(object):
    def __init__(self, gitCmd=GIT_COMMAND):
        self.command = gitCmd
        try:
            with open(os.devnull, "w") as f:
                subprocess.check_call([self.command,"--version"], stdout=f, stderr=f)
            self.exists = True
        except:
            self.exists = False
            
    def isRepo(self):
        with open(os.devnull, "w") as f:
            return bool(subprocess.call([self.command,"rev-parse"], stdout=f, stderr=f)==0)