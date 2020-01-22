#! /usr/bin/env python3

from catkin_pkg.python_setup import generate_distutils_setup
from distutils.core import setup

d = generate_distutils_setup(
    packages=['mecademic_pydriver'],
    package_dir={'': 'src'}
)

setup(**d)
