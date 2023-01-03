"""
High-level interface to MODFLOW 6.
"""

import sys

try:
    import xmipy
except ModuleNotFoundError:
    print('Please install xmipy:')
    print('    pip install xmipy')
    sys.exit()
from ._version import __version__
from .mf6 import MF6


path, ini = MF6.read_ini()
__ini_path__ = str(path)
__dll_path__ = ini['paths']['dll_path']
__xmipy_version__ = xmipy.__version__

del xmipy
