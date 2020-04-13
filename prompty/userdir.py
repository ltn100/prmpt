#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil
import errno
import distutils.dir_util


PROMPTY_USER_DIR = os.path.join(".local", "share", "prompty")
PROMPTY_CONFIG_FILE = "prompty.cfg"
SKEL_DIR = "skel"
FUNCTIONS_DIR = "functions"


def get_prompty_base_dir():
    """
    Get the directory where the prompty module is located
    """
    return os.path.dirname(
        os.path.dirname(
            # The filename of this module
            os.path.normpath(os.path.abspath(sys.modules[__name__].__file__))
        )
    )


class UserDir(object):
    def __init__(self, home_dir=None):
        if home_dir is None:
            self.home_dir = os.path.expanduser('~')
        else:
            self.home_dir = home_dir
        self.promty_user_dir = os.path.join(self.home_dir, PROMPTY_USER_DIR)
        self.promty_base_dir = get_prompty_base_dir()
        self.promty_user_functions_dir = os.path.join(self.promty_user_dir, FUNCTIONS_DIR)

        self.skel_dir = os.path.join(self.promty_base_dir, SKEL_DIR)
        if not os.path.exists(self.skel_dir):
            # Installed locally
            self.skel_dir = os.path.join(self.home_dir, ".local", "share", "prompty", SKEL_DIR)

            if not os.path.exists(self.skel_dir):
                # Install dir as defined in setup.py
                self.skel_dir = os.path.join(sys.prefix, "share", "prompty", SKEL_DIR)

                if not os.path.exists(self.skel_dir):
                    # Install dir as defined in setup.py
                    self.skel_dir = os.path.join(sys.prefix, "local", "share", "prompty", SKEL_DIR)

                if not os.path.exists(self.skel_dir):
                    raise IOError("Cannot find installed skel directory")

        # Initialise if promptyUserDir does not exist
        self.initialise()

    def initialise(self):
        if not os.path.isfile(self.get_config_file()):
            # No prompty dir - check if there is a file blocking the name
            if os.path.isfile(self.promty_user_dir):
                raise IOError("Cannot create %s directory - file exists!" % PROMPTY_USER_DIR)

            # Create prompty dir from skel
            self.copy(self.skel_dir, self.promty_user_dir)

    @staticmethod
    def copy(src, dest):
        try:
            if os.path.isdir(src):
                distutils.dir_util.copy_tree(src, dest)
            else:
                shutil.copytree(src, dest)

        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                raise IOError('Directory not copied. Error: %s' % e)

    def get_dir(self):
        return self.promty_user_dir

    def get_config_file(self):
        return os.path.join(self.promty_user_dir, PROMPTY_CONFIG_FILE)
