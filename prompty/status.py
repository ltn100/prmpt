#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess

from prompty import userdir
from prompty import vcs
from prompty import colours


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

    def inc_row(self, inc=1):
        self.row += inc

    def inc_column(self, inc=1):
        self.column += inc

    def reset_row(self):
        self.row = 0

    def reset_column(self):
        self.column = 0

    def set(self, other):
        self.column = other.column
        self.row = other.row

    def inc_from_string(self, unicode_string):
        """ Update the cursor position given movements
        from the input string. Adjust for any non-printing
        characters (these are encapsulated by the NOCOUNT_*
        characters from the Colour class)
        """
        non_print = False
        for char in unicode_string:
            if char == colours.Colours.NOCOUNT_START:
                non_print = True
                continue
            if char == colours.Colours.NOCOUNT_END:
                non_print = False
                continue
            if not non_print:
                if char == "\n":
                    self.inc_row()
                    self.reset_column()
                elif char == "\r":
                    self.reset_column()
                else:
                    self.inc_column()


class Status(object):
    def __init__(self, exit_code=0, working_dir=None):
        self.exit_code = int(exit_code)
        self.working_dir = working_dir
        self.user_dir = userdir.UserDir()
        self.euid = os.geteuid()
        self.vcs = vcs.VCS(self)
        self.wrap = True

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

    def get_working_dir(self):
        if self.working_dir:
            return os.path.normpath(self.working_dir)
        else:
            return os.path.normpath(os.getenv('PWD'))
