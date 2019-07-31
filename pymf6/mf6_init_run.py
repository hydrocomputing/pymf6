"""
Script to run MF6 for one time step

This is needed in order to generate the name-origin entries.
"""

import os
import shutil

from pymf6 import mf6
from pymf6.fortran_io import FortranValues
from pymf6 import MFSIM_NAM, BACKUP_DIR

PRINT_ALL = """
BEGIN OPTIONS
  MEMORY_PRINT_OPTION ALL
END OPTIONS
"""


def prepare_nam_file(fname=MFSIM_NAM, backup_dir=BACKUP_DIR):
    """
    Create name file that saves all MF6 nam-origin pairs in lst file
    :param fname: `mfsim.nam`
    :param backup_dir: ``backup directory for `mfsim.nam`
    :return: None
    """
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    fname_backup = os.path.join(backup_dir, fname)
    shutil.copy(fname, fname_backup)
    do_write = True
    with open(fname, 'w') as fobj_out, open(fname_backup) as fobj_in:
        fobj_out.write(PRINT_ALL)
        for line in fobj_in:
            if line.strip().upper().startswith('BEGIN OPTIONS'):
                do_write = False
            if line.strip().upper().startswith('END OPTIONS'):
                do_write = True
                continue
            if do_write:
                fobj_out.write(line)


def restore_name_file(fname=MFSIM_NAM, backup_dir=BACKUP_DIR):
    """
    Restore `mfsim.nam` file.
    :param fname: `mfsim.nam`
    :param backup_dir: ``ackup directory for `mfsim.nam`
    :return: None
    """
    shutil.copy(os.path.join(backup_dir, fname), fname)


class Func:
    # pylint: disable=too-few-public-methods
    """
    Callback that runs only for one time step by default.

    Provide `stop` to specify the maximum number of time steps.
    Defaults to 1.
    """

    def __init__(self, stop=1):
        self.counter = 0
        self.stop = stop
        mf6_data_type_table = {
            ('ENDOFSIMULATION', 'TDIS'): {'data_type': 'bool_scalar'}
        }
        fort = FortranValues(mf6_data_type_table=mf6_data_type_table).set_value
        self.set_value = fort

    def __call__(self):
        self.counter += 1
        print(self.counter)
        if self.counter >= self.stop:
            restore_name_file()
            self.set_value('ENDOFSIMULATION', 'TDIS', True)


def main():
    """
    Main function for initial run
    """
    prepare_nam_file()
    mf6.mf6_sub(Func())


if __name__ == '__main__':
    main()
