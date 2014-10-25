#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import subprocess

import vcs


class Coords(object):
    def __init__(self, column=0, row=0):
        self.column = column
        self.row = row

    def __iadd__(self, other):
        self.column += other.column
        self.row += other.row
        return self

    def __add__(self, other):
        return Coords(self.column+other.column,
                      self.row+other.row)

    def incRow(self, inc=1):
        self.row += inc

    def incColumn(self, inc=1):
        self.column += inc

    def set(self,other):
        self.column = other.column
        self.row = other.row


class Status(object):
    def __init__(self, exitCode=0, workingDir=None):
        self.exitCode = int(exitCode)
        self.workingDir = workingDir
        self.euid = os.geteuid()
        self.vcs = vcs.VCS(self)
        
        proc = subprocess.Popen(['stty', 'size'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
        if proc.returncode == 0:
            dims = stdout.split()
            self.window = Coords(int(dims[1]),int(dims[0]))
        else:
            self.window = Coords()
        self.pos = Coords()

    def getWorkingDir(self):
        if self.workingDir:
            return os.path.normpath(self.workingDir)
        else:
            return os.path.normpath(os.getenv('PWD'))
