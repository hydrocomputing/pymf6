"""Main"""

import pymf6


def info():
    """Show version and paths information"""
    print(f'PyMF6 version: {pymf6.__version__}')
    print(f'XMIPy version: {pymf6.__xmipy_version__}')
    print(f'Ini file path: {pymf6.__ini_path__}')
    print(f'DLL file path: {pymf6.__dll_path__}')


if __name__ == '__main__':
    info()
