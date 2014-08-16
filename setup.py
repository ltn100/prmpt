#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.build_py import build_py
import py_compile
import glob
import os


class PostBuild(build_py):
    def run(self):
        build_py.run(self)
        print "compiling promptyc"
        py_compile.compile('bin/prompty')


setup(name='prompty',
    # Must comply with http://legacy.python.org/dev/peps/pep-0440/#version-scheme
    version='0.1rc1',

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
    ],

    cmdclass={
        # Post build step
        'build_py': PostBuild,
    },
)

