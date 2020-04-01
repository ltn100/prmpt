#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Import external modules


# Import prompty modules
from prompty import functionContainer
from prompty import compiler
from prompty import config
from prompty import functions
from prompty import colours
from prompty import vcs


class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.funcs = functionContainer.FunctionContainer(
            self.status
        )
        self.funcs.addFunctionsFromModule(functions)
        self.funcs.addFunctionsFromModule(colours)
        self.funcs.addFunctionsFromModule(vcs)
        self.funcs.addFunctionsFromDir(self.status.userDir.promtyUserFunctionsDir)

        self.compiler = compiler.Compiler(self.funcs)
        self.config = config.Config()
        self.config.load(self.status.userDir.getConfigFile())

    def getPrompt(self):
        self.compiler.compile(self.config.promptString)
        output = self.compiler.execute()
        return output
