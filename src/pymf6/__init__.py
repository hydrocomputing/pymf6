"""
High-level interface to MODFLOW 6.
"""

from pathlib import Path
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
__ini_path__ = str(path) if path else path
if ini:
    __dll_path__ = ini['paths']['dll_path']
    if not Path(__dll_path__).exists():
        raise ValueError(
            f'dll path `{__dll_path__}` does not exist\n'
            'Please specify correct path.'
            )
else:
    __dll_path__ = None
__xmipy_version__ = xmipy.__version__

del xmipy
