"""Main"""

from os import sep
import sys
import textwrap

import pymf6


def info():
    """Show version and paths information"""
    header = 'pymf6 configuration data'
    ini_path = pymf6.__ini_path__
    print(header)
    print('=' * len(header))
    print(f'pxmf6 version: {pymf6.__version__}')
    print(f'xmipy version: {pymf6.__xmipy_version__}')
    print(f'ini file path: {ini_path}')
    print(f'dll file path: {pymf6.__dll_path__}')

    if ini_path is None:
        if sys.platform == 'win32':
            find_home = 'set HOMEPATH'
            ext = 'dll'
        else:
            find_home = 'echo $HOME'
            ext = 'so'
            if sys.platform == 'darwin':
                ext = 'dylib'
        print(textwrap.dedent(f"""
        No configuration file found. Need to specify the path to the
        MODFLOW 6 DLL for each run. Consider using a configuration file
        `pymf6.ini` for more convenience.

        Specify the DLL path in file `pymf6.ini`.
        Put a file named `pymf6.ini` in your home directory.
        You can find your home path with the command:

            {find_home}

        The content of `pymf6.ini` should be:

            [paths]
            dll_path = path{sep}to{sep}mf6{sep}bin{sep}libmf6.{ext}

        Replace the path with with your absolute path to the MODFLOW 6
        directory `bin` that contains the shared library, i.e. the file
        `libmf6.{ext}`.
        """))


if __name__ == '__main__':
    info()
