#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import os
import ConfigParser

class Config(object):
    def __init__(self):
        self.promptString = ""
        self.configFile = None
        self.configDir = None
        self.configParser = ConfigParser.SafeConfigParser()
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

    def loadPromptFile(self):
        with open (self.promptFile, "rb") as pFile:
            self.promptString = pFile.read()
            