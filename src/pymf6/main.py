"""Main"""

from os import sep
from pathlib import Path
import sys
import textwrap

import pymf6


def info():
    """Show version and paths information"""
    header = 'pymf6 configuration data'
    ini_path = pymf6.__ini_path__
    dll_path = pymf6.__dll_path__
    print(header)
    print('=' * len(header))
    print(f'pxmf6 version: {pymf6.__version__}')
    print(f'xmipy version: {pymf6.__xmipy_version__}')
    print(f'ini file path: {ini_path}')
    print(f'dll file path: {dll_path}')
    if dll_path:
        mf6 = pymf6.MF6(dll_path=dll_path)
        print(f'MODFLOW version: {mf6.version}')

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

def run_model(nam_file):
    """Run one model without modifications."""
    text = f'running {nam_file}'
    line = '=' * len(text)
    print(line)
    print(text)
    print(line)
    try:
        mf6 = pymf6.MF6(nam_file=nam_file)
        for step in mf6.steps():
            pass
        print(f'GOOD {nam_file}')
    except:
        print(f'BAD {nam_file}')
        raise
    print(line)
    print(line)


def main():
    """Main program of pymf6"""
    args = sys.argv
    if len(args) == 2:
        run_model(args[1])
    else:
        info()


if __name__ == '__main__':
    main()

