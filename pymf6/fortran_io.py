"""Read and write Fortran values from MF6.
"""

from pymf6.mfnames import get_names
from . import mf6


MF6_DATA_TYPE_TABLE = get_names()


def get_bool(name, origin):
    """Get a boolean value.
    """
    mf6.access_memory.get_bool(name, origin)
    return mf6.shared_data.bool_scalar


def get_int(name, origin):
    """Get an integer scalar.
    """
    mf6.access_memory.get_int(name, origin)
    return mf6.shared_data.int_scalar


def get_float(name, origin):
    """Get an float scalar.
    """
    mf6.access_memory.get_float(name, origin)
    return mf6.shared_data.float_scalar


def get_int_1d(name, origin):
    """Get a 1d integer array.
    """
    mf6.access_memory.get_int_1d(name, origin)
    return mf6.shared_data.int_1d


def get_float_1d(name, origin):
    """Get a 1d float array.
    """
    mf6.access_memory.get_float_1d(name, origin)
    return mf6.shared_data.float_1d


def get_int_2d(name, origin):
    """Get a 2d integer array.
    """
    mf6.access_memory.get_int_2d(name, origin)
    return mf6.shared_data.int_2d


def get_float_2d(name, origin):
    """Get a 2d float array.
    """
    mf6.access_memory.get_float_2d(name, origin)
    return mf6.shared_data.float_2d


READING_FUNCTIONS = {
    'bool_scalar': get_bool,
    'int_scalar': get_int,
    'float_scalar': get_float,
    'int_1d': get_int_1d,
    'float_1d': get_float_1d,
    'int_2d': get_int_2d,
    'float_2d': get_float_2d,
    }


WRITING_FUNCTIONS = {
    'bool_scalar': mf6.access_memory.set_bool,
    'int_scalar': mf6.access_memory.set_int,
    'float_scalar': mf6.access_memory.set_float,
    'int_1d': mf6.access_memory.set_int_1d,
    'float_1d': mf6.access_memory.set_float_1d,
    'int_2d': mf6.access_memory.set_int_2d,
    'float_2d': mf6.access_memory.set_float_2d,
    }


def get_value(name, origin):
    """Get the value for any dimension and data type.
    """
    entry = MF6_DATA_TYPE_TABLE[(name, origin)]
    data_type = entry['data_type']
    func = READING_FUNCTIONS[data_type]
    return func(name, origin)


def set_value(name, origin, value):
    """Set the value of any dimension and data type.
    """
    entry = MF6_DATA_TYPE_TABLE[(name, origin)]
    data_type = entry['data_type']
    func = WRITING_FUNCTIONS[data_type]
    func(name, origin, value)
