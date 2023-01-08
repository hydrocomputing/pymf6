from configparser import ConfigParser
from pathlib import Path
import os
import textwrap
import sys

import xmipy

from .. _version import __version__


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


def get_infos():
    """Find all versions."""
    infos = {}
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
    infos['ini_path'] = ini_path
    infos['dll_path'] = dll_path
    infos['xmipy_version'] = xmipy.__version__
    infos['pymf6_version'] = __version__
    if dll_path:
        infos['modflow_version'] = xmipy.XmiWrapper(str(dll_path)).get_version()

    if ini_path is None:
        if sys.platform == 'win32':
            infos['_find_home'] = 'set HOMEPATH'
            infos['_ext'] = 'dll'
            infos['_sep'] = os.sep
        else:
            infos['_find_home'] = 'echo $HOME'
            infos['_ext'] = 'so'
            if sys.platform == 'darwin':
                infos['_ext'] = 'dylib'
    return infos


def info():
    """Show version and paths information"""
    header = 'pymf6 configuration data'
    infos = get_infos()
    print(header)
    print('=' * len(header))
    print(f'pymf6 version: {infos["pymf6_version"]}')
    print(f'xmipy version: {infos["xmipy_version"]}')
    print(f'ini file path: {infos["ini_path"]}')
    print(f'dll file path: {infos["dll_path"]}')
    if 'modflow_version' in infos:
        print(f'MODFLOW version: {infos["modflow_version"]}')
    if infos['ini_path'] is None:
        sep = infos['_sep']
        ext = infos['_ext']
        print(textwrap.dedent(f"""
        No configuration file found. Need to specify the path to the
        MODFLOW 6 DLL for each run. Consider using a configuration file
        `pymf6.ini` for more convenience.

        Specify the DLL path in file `pymf6.ini`.
        Put a file named `pymf6.ini` in your home directory.
        You can find your home path with the command:

            {infos['_find_home']}

        The content of `pymf6.ini` should be:

            [paths]
            dll_path = path{sep}to{sep}mf6{sep}bin{sep}libmf6.{ext}

        Replace the path with with your absolute path to the MODFLOW 6
        directory `bin` that contains the shared library, i.e. the file
        `libmf6.{ext}`.
        """))

