#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='h2lily',
      version='0.1',
      description='Export and engrave Hydrogen drum pattern to Lilypond sheet',
      url='http://github.com/thomasfillon/h2lily',
      author='Thomas Fillon',
      author_email='thomas@parisson.com',
      license='GPL2.0',
      packages=['h2lily'],
      entry_points={
          "console_scripts": ['h2lily = h2lily.h2lily:main']
          },
      zip_safe=False,
      install_requires=['docopt'])
