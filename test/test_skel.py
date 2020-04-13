#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from test import prompty
from test import UnitTestWrapper

import os
import sys


class SkelTests(UnitTestWrapper):

    def test_skelFiles(self):
        print()
        test_dir = os.path.dirname(os.path.abspath(__file__))
        all_files = os.listdir(os.path.join(test_dir, "..", "skel"))
        files = [os.path.join(test_dir, "..", "skel", f) for f in all_files if f.endswith(".prompty")]
        for file in files:
            p = prompty.prompt.Prompt(prompty.status.Status())
            p.config.prompt_file = file
            p.config.load_prompt_file()
            s = p.get_prompt()
            print("Testing " + file)
            print(s.replace(prompty.colours.Colours.NOCOUNT_START, '').replace(prompty.colours.Colours.NOCOUNT_END, ''))
            print()
        self.assertEqual(1, 1)
