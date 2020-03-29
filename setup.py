#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import setuptools
from setuptools.command.build_py import build_py
import py_compile
import glob
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class PostBuild(build_py):
    def run(self):
        build_py.run(self)
        print("compiling promptyc")
        py_compile.compile('bin/prompty')


setuptools.setup(
    name="prompty",
    version=find_version("prompty", "__init__.py"),
    description="A command line prompt markup language",
    author="Lee Netherton",
    author_email="lee.netherton@gmail.com",
    url="https://github.com/ltn100/prompty",
    license="MIT licence, see LICENCE",

    packages=["prompty"],

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: Terminals",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
        "Topic :: Utilities",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Operating System :: MacOS"
    ],

    scripts=["bin/prompty"],

    data_files=[
        (
            "share/prompty/skel",
            [f for f in glob.glob("skel/*") if os.path.isfile(f)]
        ),
        (
            "share/prompty/skel/functions",
            [f for f in glob.glob("skel/functions/*") if os.path.isfile(f)]
        ),
    ],

    cmdclass={
        # Post build step
        "build_py": PostBuild,
    },

    setup_requires=[
        "wheel"
    ],

    install_requires=[
        "future",
        "configparser"
    ],
)
