#!/usr/bin/env python

from distutils.core import setup

setup(name='Sonar CLI',
      version='1.0',
      description='Command line interface to communicate with the project sonar open data.',
      packages=['sonar'],
      entry_points={
          'console_scripts': ['sonar=sonar:cli'],
      })
