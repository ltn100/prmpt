#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import sys

# Import prompty modules
import parser
import compiler
import userdir


def getPromptyBaseDir():
    return os.path.dirname(
        os.path.dirname(
            # The filename of this module
            sys.modules[__name__].__file__
        )
    )


class Status(object):
    def __init__(self, exitCode=0):
        self.exitCode = int(exitCode)
        self.euid = os.geteuid()


class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.parser = parser.Parser()
        self.compiler = compiler.Compiler(status)
        self.userDir = userdir.UserDir()


    def getPrompt(self):
        return self.compiler.compile(self.parser.parse(
            r"""
            \green{
                \user
            }
            @
            \white{
                \hostname
            }
            \space
            \blue[bold]{
                \workingdir
            }
            \newline
            \smiley
            \space
            """
        ))





