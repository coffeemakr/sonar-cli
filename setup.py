#!/usr/bin/env python

from distutils.core import setup

import pathlib

import pkg_resources

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


setup(name='Sonar CLI',
      version='1.0',
      description='Command line interface to communicate with the project sonar open data.',
      packages=['sonar'],
      entry_points={
          'console_scripts': ['sonar=sonar:cli'],
      },
      install_requires=install_requires)
