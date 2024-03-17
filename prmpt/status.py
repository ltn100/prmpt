#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess

from prmpt import userdir
from prmpt import vcs
from prmpt import colours


class Coords(object):
    """ Cursor coordinates
    """
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

    def resetRow(self):
        self.row = 0

    def resetColumn(self):
        self.column = 0

    def set(self, other):
        self.column = other.column
        self.row = other.row

    def incFromString(self, unicodeString):
        """ Update the cursor position given movements
        from the input string. Adjust for any non-printing
        characters (these are encapsulated by the NOCOUNT_*
        characters from the Colour class)
        """
        non_print = False
        for char in unicodeString:
            if char == colours.Colours.NOCOUNT_START:
                non_print = True
                continue
            if char == colours.Colours.NOCOUNT_END:
                non_print = False
                continue
            if not non_print:
                if char == "\n":
                    self.incRow()
                    self.resetColumn()
                elif char == "\r":
                    self.resetColumn()
                else:
                    self.incColumn()


class Status(object):
    def __init__(self, exitCode=0, workingDir=None):
        self.exitCode = int(exitCode)
        self.workingDir = workingDir
        self.userDir = userdir.UserDir()
        self.euid = os.geteuid()
        self.vcs = vcs.VCS(self)

        proc = subprocess.Popen(['stty', 'size'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
        if proc.returncode == 0:
            dims = stdout.split()
            self.window = Coords(int(dims[1]), int(dims[0]))
        else:
            self.window = Coords()
        self.pos = Coords()

    def getWorkingDir(self):
        if self.workingDir:
            return os.path.normpath(self.workingDir)
        else:
            return os.path.normpath(os.getenv('PWD'))
