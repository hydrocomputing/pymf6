"""Read and write Fortran values from MF6.
"""


from . import mf6


# Put this into a file?

MF6_DATA_TYPE_TABLE = {
    ('NPER', 'TDIS'): {'data_type': 'int_scalar'},
    ('DELT', 'TDIS'): {'data_type': 'float_scalar'},
    ('NSTP', 'TDIS'): {'data_type': 'int_1d'},
    ('PERLEN', 'TDIS'): {'data_type': 'float_1d'},
    ('LRCH', 'SLN_1'): {'data_type': 'int_2d'},
    ('MXITER', 'SLN_1'): {'data_type': 'int_scalar'},
    ('AUXVAR', 'GWF_1 WEL'): {'data_type': 'float_2d'},
    ('NAUX', 'GWF_1 WEL'): {'data_type': 'int_scalar'},
    ('MAXBOUND', 'GWF_1 WEL'): {'data_type': 'int_scalar'},
}


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
    'int_scalar': get_int,
    'float_scalar': get_float,
    'int_1d': get_int_1d,
    'float_1d': get_float_1d,
    'int_2d': get_int_2d,
    'float_2d': get_float_2d,
    }


WRITING_FUNCTIONS = {
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
