#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import sys

# Import prompty modules
import parser
import functionContainer
import compiler
import userdir
import config
import git


def getPromptyBaseDir():
    return os.path.dirname(
        os.path.dirname(
            # The filename of this module
            os.path.normpath(os.path.abspath(sys.modules[__name__].__file__))
        )
    )


class Status(object):
    def __init__(self, exitCode=0):
        self.exitCode = int(exitCode)
        self.euid = os.geteuid()
        self.git = git.Git()


class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.userDir = userdir.UserDir()
        self.funcs = functionContainer.FunctionContainer(self.status, [self.userDir.promtyUserFunctionsDir])
        self.compiler = compiler.Compiler(self.funcs)
        self.config = config.Config()
        self.config.load(self.userDir.getConfigFile())


    def getPrompt(self):
        return self.compiler.compile(
                    self.config.promptString
                )





