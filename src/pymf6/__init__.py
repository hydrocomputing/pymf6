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

infos = get_info()

__ini_path__ = infos['ini_path']
__dll_path__ = infos['dll_path']
__xmipy_version__ = infos['xmipy_version']
__version__ = __pymf6_version__ = infos['pymf6_version']
__modflow_version__ = infos['modflow_version']

del xmipy
