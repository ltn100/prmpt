#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules


# Import prompty modules
import functionContainer
import compiler
import userdir
import config


class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.userDir = userdir.UserDir()
        self.funcs = functionContainer.FunctionContainer(
            self.status, [self.userDir.promtyUserFunctionsDir]
        )
        self.compiler = compiler.Compiler(self.funcs)
        self.config = config.Config()
        self.config.load(self.userDir.getConfigFile())


    def getPrompt(self):
        self.compiler.compile(self.config.promptString)
        return self.compiler.execute()
