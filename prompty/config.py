#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import glob
from configparser import ConfigParser


class Config(object):
    def __init__(self):
        self.prompt_string = ""
        self.config_file = None
        self.config_dir = None
        self.config_parser = ConfigParser()
        self.prompt_file = None

    def load(self, filename):
        self.config_file = filename
        self.config_dir = os.path.dirname(filename)

        # Read and parse the config file
        self.config_parser.read(filename)

        self.prompt_file = self.get_prompt_file_path()

        self.load_prompt_file(self.get_prompt_file_path())

    def get_prompt_file_path(self, name=None):
        if name is None:
            # Get name from config
            name = self.config_parser.get('prompt', 'prompt_file')

        suggestion = name
        if os.path.isfile(suggestion):
            return suggestion

        suggestion = os.path.join(self.config_dir, name)
        if os.path.isfile(suggestion):
            return suggestion

        suggestion = os.path.join(self.config_dir, name+".prompty")
        if os.path.isfile(suggestion):
            return suggestion

        return None

    def save(self):
        with open(self.config_file, 'w') as f:
            self.config_parser.write(f)

    def load_prompt_file(self, filename=None):
        if filename is None:
            filename = self.prompt_file

        with open(filename, "r") as f:
            self.prompt_string = f.read()

    def get_prompt_files(self):
        return sorted(
            glob.glob(
                os.path.join(self.config_dir, "*.prompty")
            )
        )
