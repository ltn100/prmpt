#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules


# Import prompty modules
import functionContainer
import compiler
import config
import functions
import colours
import vcs

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
        return self.compiler.execute()
