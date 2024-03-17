#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import unittest

from test.test_prmpt import *
from test.test_parser import *
from test.test_colours import *
from test.test_functionContainer import *
from test.test_functions import *
from test.test_vcs import *
from test.test_skel import *


if __name__ == "__main__":
    print("Prmpt module path: %s" % prmpt.__path__[0])
    sys.exit(unittest.main())
