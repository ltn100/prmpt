#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
        self.funcs.add_functions_from_module(functions)
        self.funcs.add_functions_from_module(colours)
        self.funcs.add_functions_from_module(vcs)
        self.funcs.add_functions_from_dir(self.status.user_dir.promty_user_functions_dir)

        self.compiler = compiler.Compiler(self.funcs)
        self.config = config.Config()
        self.config.load(self.status.user_dir.get_config_file())

    def get_prompt(self):
        self.compiler.compile(self.config.prompt_string)
        output = self.compiler.execute()
        return output
