#!/usr/local/bin/python
# coding: utf-8

"""
Build a conda package.
"""


from setuptools import setup, find_packages
import sys


from pymf6 import __version__, __name__, __author__

extras = ''

if sys.platform == 'win32':
    mf6_fortran = 'mf6.cp37-win_amd64.pyd'
elif sys.platform == 'darwin':
    mf6_fortran = 'mf6.cp37.cpython-37m-darwin.so'
    extras = 'libgfortran.4.dylib'
elif sys.platform.startswith('linux'):
    mf6_fortran = 'mf6.cpython-37m-x86_64-linux-gnu.so'
else:
    raise Exception(f'Platform {sys.platform} not supported.')


setup(
      name=__name__,
      version=__version__,
      url='https://github.com/hydrocomputing/pymf6',
      license='MIT',
      author=__author__,
      author_email='mmueller@hydrocomputing.com',
      description='Python Wrapper for MODFLOW 6',
      long_description=open('README.md').read(),
      packages = find_packages(),
      platforms='any',
      install_requires=['numpy'],
      package_data={'': ['pymf6', '*.pyd', mf6_fortran, extras]},
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Hydrology'
    ]
)



