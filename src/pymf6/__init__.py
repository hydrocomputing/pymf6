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

from .tools.infos import get_infos

infos = get_infos()

__ini_path__ = infos['ini_path']
__dll_path__ = infos['dll_path']
__xmipy_version__ = infos['xmipy_version']
__version__ = infos['pymf6_version']
__infos__ = ['modflow_version']

del xmipy
