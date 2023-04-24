"""
Find all version infos and paths.

The versions include:

* MODFLOW 6
* xmipy
* pymf6

The paths include:

* ini path
* dll path
* MODFLOW 6 doc path
"""


from configparser import ConfigParser
from pathlib import Path
import os
import textwrap
import sys

import xmipy

import pymf6
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


def get_info_data():
    """Find all versions."""
    info = {}
    path, ini = read_ini()
    ini_path = Path(path) if path else path
    if ini:
        dll_path = Path(ini['paths']['dll_path'])
        if not dll_path.exists():
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
    info['modflow_version'] = None
    info['mf6_doc_path'] = None
    if dll_path:
        mf6_version = xmipy.XmiWrapper(str(dll_path)).get_version()
        info['modflow_version'] = mf6_version
        mf6_doc_path = (
            Path(pymf6.__file__).parent / 'resources/mf6_var_names/mem_vars')
        mf6_doc_path = mf6_doc_path / f'{mf6_version}'
        info['mf6_doc_path'] = mf6_doc_path if mf6_doc_path.exists() else None

    if ini_path is None:
        info['_sep'] = os.sep
        if sys.platform == 'win32':
            info['_find_home'] = 'set HOMEPATH'
            info['_ext'] = 'dll'
        else:
            info['_find_home'] = 'echo $HOME'
            info['_ext'] = 'so'
            if sys.platform == 'darwin':
                info['_ext'] = 'dylib'
    return info


def make_info_texts(info_data=None, demo=False):
    """Show version and paths information"""
    if info_data is None:
        info_data= get_info_data()
    info_texts = {}
    info_texts['header'] = 'pymf6 configuration data'
    info_texts['entries'] = [
        ('pymf6 version', f'{info_data["pymf6_version"]}'),
        ('xmipy version', f'{info_data["xmipy_version"]}'),
    ]
    if demo:
        info_texts['entries'].extend([
            ('ini file path', 'HOME/pymf6.ini'),
            ('dll file path', 'path/to/dll/libmf6.dll'),
            ])
    else:
        info_texts['entries'].extend([
            ('ini file path', f'{info_data["ini_path"]}'),
            ('dll file path', f'{info_data["dll_path"]}'),
            ])
    if info_data["modflow_version"]:
        info_texts['entries'].append(
            ('MODFLOW version', f'{info_data["modflow_version"]}')
        )
    has_docs = 'is  NOT'
    if info_data['mf6_doc_path']:
        has_docs = 'is'
    info_texts['mf_docs_info'] = (
        f'MODFLOW variable documentation {has_docs} available')
    info_texts['config_hint'] = None
    if info_data['ini_path'] is None:
        sep = info_data['_sep']
        ext = info_data['_ext']
        info_texts['config_hint'] = textwrap.dedent(f"""
        No configuration file found. Need to specify the path to the
        MODFLOW 6 DLL for each run. Consider using a configuration file
        `pymf6.ini` for more convenience.

        Specify the DLL path in file `pymf6.ini`.
        Put a file named `pymf6.ini` in your home directory.
        You can find your home path with the command:

            {info_data['_find_home']}

        The content of `pymf6.ini` should be:

            [paths]
            dll_path = path{sep}to{sep}mf6{sep}bin{sep}libmf6.{ext}

        Replace the path with with your absolute path to the MODFLOW 6
        directory `bin` that contains the shared library, i.e. the file
        `libmf6.{ext}`.
        """)
    return info_texts


def make_info_html(info_texts=None):
    """Create version and path info as HTML."""
    if info_texts is None:
        info_texts = make_info_texts()
    html_text = '<h3>MF6</h3>'
    html_text += f'<h4>{info_texts["header"]}</h4>'
    html_text += '<table><tbody>'
    for name, value in info_texts['entries']:
        html_text += f'<tr><td>{name}:</td>'
        html_text += f'<td>{value}</td></tr>'
    html_text += '</tbody></table>'
    html_text += f'<p>{info_texts["mf_docs_info"]}</p>'
    if info_texts['config_hint']:
        html_text += f'<p>{info_texts["config_hint"]}</p>'
    return html_text


def show_info(info_texts=None):
    """Show verion and path info as text."""
    if info_texts is None:
        info_texts = make_info_texts()
    header = info_texts['header']
    print('=' * len(header))
    print(header)
    print('=' * len(header))
    for line in info_texts['entries']:
        print(*line, sep=': ')
    print(info_texts['mf_docs_info'])
    if info_texts['config_hint']:
        print(info_texts['config_hint'])
