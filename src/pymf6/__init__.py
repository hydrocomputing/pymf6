"""High-level interface to MODFLOW 6."""

from .tools.info import get_info_data

info = get_info_data()

__ini_path__ = info['ini_path']
__dll_path__ = info['dll_path']
__xmipy_version__ = info['xmipy_version']
__version__ = __pymf6_version__ = info['pymf6_version']
__modflow_version__ = info.get('modflow_version')
__mf6_exe__ = info.get('exe_path')
__model_prefixes__ = {
    'flow': 'gwf_',
    'transport': 'gwt_',
    'energy': 'gwe_',
    }
