#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

from distutils.core import setup
import glob
import os

setup(name='prompty',
      version='0.1',
      description='A command line prompt markup language',
      author='Lee Netherton',
      author_email='lee.netherton@gmail.com',
      url='https://github.com/ltn100/prompty',
      license='MIT licence, see LICENCE',
      packages=['prompty'],
      scripts=['bin/prompty','bin/promptyc'],
      data_files=[
        ('share/prompty/skel',
         [f for f in glob.glob("skel/*") if os.path.isfile(f)]
         ),
        ('share/prompty/skel/functions',
         [f for f in glob.glob("skel/functions/*") if os.path.isfile(f)]
         ),
      ]
     )
