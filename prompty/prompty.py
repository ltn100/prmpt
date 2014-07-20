#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os


import parser
import compiler





class Status(object):
    def __init__(self, exitCode=0):
        self.exitCode = int(exitCode)
        self.euid = os.geteuid()


class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.parser = parser.Parser()
        self.compiler = compiler.Compiler(status)


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





