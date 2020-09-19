"""
Python Wrapper for MODFLOW 6
"""

from multiprocessing import Process

from . mf6 import mf6_sub  # pylint: disable-msg=no-name-in-module

__all__ = ['__version__', '__name__', '__author__']

__version__ = '0.5.0'
__name__ = 'pymf6'  # pylint: disable=redefined-builtin
__author__ = 'Mike Müller'

MFSIM_NAM = 'mfsim.nam'
BACKUP_DIR = '__pymf6__backup'
DATA_MAPPING = 'data_mapping.pkl'


def func(callback, kwargs):
    """Helper function for run with `multiprocessing`
    """
    from pymf6.callback import Func
    
    class MyFunc(callback, Func):
         pass

    if kwargs is None:
        kwargs = {}
        
    mf6_sub(MyFunc(**kwargs))


def run(callback, kwargs):
    """Run the MF6 model in the current paths with `callback`
    """

    
    process = Process(target=func, args=(callback, kwargs))
    process.start()
    process.join()
