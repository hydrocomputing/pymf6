"""
Python Wrapper for MODFLOW 6
"""

from multiprocessing import Process

from . mf6 import mf6_sub  # pylint: disable-msg=no-name-in-module

__all__ = ['__version__', '__name__', '__author__']

__version__ = '0.4.2'
__name__ = 'pymf6'  # pylint: disable=redefined-builtin
__author__ = 'Mike Müller'

MFSIM_NAM = 'mfsim.nam'
BACKUP_DIR = '__pymf6__backup'
DATA_MAPPING = 'data_mapping.pkl'


def run(callback):
    """Run the MF6 model in the current paths with `callback`
    """

    def func():
        """Helper function for run with `multiprocessing`
        """
        mf6_sub(callback)

    process = Process(target=func)
    process.start()
    process.join()
