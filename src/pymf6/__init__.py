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

from .tools.info import get_info

info = get_info()

__ini_path__ = info['ini_path']
__dll_path__ = info['dll_path']
__xmipy_version__ = info['xmipy_version']
__version__ = __pymf6_version__ = info['pymf6_version']
if 'modflow_version' in info:
    __modflow_version__ = info['modflow_version']

del xmipy
