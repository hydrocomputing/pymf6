
import os
import platform

from pymf6.tools.info import read_ini


def test_arch():
    real_arch = platform.uname().machine
    for arch in ['', f'_{real_arch}']:
        dll_file_name = f'{arch}.dylib'
        ini_file_name = 'pymf6.ini'
        with open(ini_file_name, 'w', encoding='utf-8') as fobj:
            fobj.write(f"""[paths{arch}]
            dll_path = {dll_file_name}""")
        with open(dll_file_name, 'w', encoding='utf-8'):
            pass
        ini_data = read_ini()
        assert str(ini_data['dll_path']).startswith(arch)
        os.remove(ini_file_name)
        os.remove(dll_file_name)
