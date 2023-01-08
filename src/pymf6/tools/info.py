from configparser import ConfigParser
from pathlib import Path
import os
import textwrap
import sys

import xmipy

from .._version import __version__


def read_ini():
    """Read ini file.

    This looks for `pymf6.ini` in the current working directory
    first. If not found there, it looks in the user's home directory.
    If no file is found `ini_data` will be `None`.
    """
    ini_path = Path('pymf6.ini')
    if not ini_path.exists():
        ini_path = ini_path.home() / ini_path
    if not ini_path.exists():
        ini_path = None
    if ini_path:
        ini_path = ini_path.resolve()
        parser = ConfigParser()
        parser.read(ini_path)
        ini_data = parser
    else:
        ini_data = None
    return ini_path, ini_data


def get_info():
    """Find all versions."""
    info = {}
    path, ini = read_ini()
    ini_path = str(path) if path else path
    if ini:
        dll_path = ini['paths']['dll_path']
        if not Path(dll_path).exists():
            raise ValueError(
                f'dll path `{dll_path}` does not exist\n'
                'Please specify correct path.'
                )
    else:
        dll_path = None
    info['ini_path'] = ini_path
    info['dll_path'] = dll_path
    info['xmipy_version'] = xmipy.__version__
    info['pymf6_version'] = __version__
    if dll_path:
        info['modflow_version'] = xmipy.XmiWrapper(str(dll_path)).get_version()

    if ini_path is None:
        if sys.platform == 'win32':
            info['_find_home'] = 'set HOMEPATH'
            info['_ext'] = 'dll'
            info['_sep'] = os.sep
        else:
            info['_find_home'] = 'echo $HOME'
            info['_ext'] = 'so'
            if sys.platform == 'darwin':
                info['_ext'] = 'dylib'
    return info


def info(info=None):
    """Show version and paths information"""
    header = 'pymf6 configuration data'
    if info is None:
        info = get_info()
    print(header)
    print('=' * len(header))
    print(f'pymf6 version: {info["pymf6_version"]}')
    print(f'xmipy version: {info["xmipy_version"]}')
    print(f'ini file path: {info["ini_path"]}')
    print(f'dll file path: {info["dll_path"]}')
    if 'modflow_version' in info:
        print(f'MODFLOW version: {info["modflow_version"]}')
    if info['ini_path'] is None:
        sep = info['_sep']
        ext = info['_ext']
        print(textwrap.dedent(f"""
        No configuration file found. Need to specify the path to the
        MODFLOW 6 DLL for each run. Consider using a configuration file
        `pymf6.ini` for more convenience.

        Specify the DLL path in file `pymf6.ini`.
        Put a file named `pymf6.ini` in your home directory.
        You can find your home path with the command:

            {info['_find_home']}

        The content of `pymf6.ini` should be:

            [paths]
            dll_path = path{sep}to{sep}mf6{sep}bin{sep}libmf6.{ext}

        Replace the path with with your absolute path to the MODFLOW 6
        directory `bin` that contains the shared library, i.e. the file
        `libmf6.{ext}`.
        """))

