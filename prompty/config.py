#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from configparser import ConfigParser


class Config(object):
    def __init__(self):
        self.promptString = ""
        self.configFile = None
        self.configDir = None
        self.configParser = ConfigParser()
        self.promptFile = None

    def load(self, filename):
        self.configFile = filename
        self.configDir = os.path.dirname(filename)

        # Read and parse the config file
        self.configParser.read(filename)

        self.promptFile = os.path.join(
            self.configDir,
            self.configParser.get('prompt', 'prompt_file')
        )

        self.loadPromptFile()

    def save(self):
        with open(self.configFile, 'w') as f:
            self.configParser.write(f)

    def loadPromptFile(self):
        with open(self.promptFile, "r") as pFile:
            self.promptString = pFile.read()
