"""Read and write Fortran values from MF6.
"""

from pymf6.mfnames import get_names
from . import mf6

TIME_UNIT_NAMES = ('UNDEFINED', 'SECONDS', 'MINUTES', 'HOURS', 'DAYS', 'YEARS')
TIME_UNIT_VALUES = (None, 1, 60, 3600, 86400, 31557600)
LENGTH_UNIT_NAMES = ('UNDEFINED', 'FEET', 'METERS', 'CENTIMETERS')


class FortranValues:
    """
    Reading and writing of MF6 values
    """
    def __init__(self, mf6_data_type_table=None, verbose=False):
        if not mf6_data_type_table:
            mf6_data_type_table = get_names(verbose=verbose)
        self.mf6_data_type_table = mf6_data_type_table

        self.reading_functions = {
            'bool_scalar': self._get_bool,
            'int_scalar': self._get_int,
            'float_scalar': self._get_float,
            'int_1d': self._get_int_1d,
            'float_1d': self._get_float_1d,
            'int_2d': self._get_int_2d,
            'float_2d': self._get_float_2d,
        }

        self.writing_functions = {
            'bool_scalar': mf6.access_memory.set_bool,
            'int_scalar': mf6.access_memory.set_int,
            'float_scalar': mf6.access_memory.set_float,
            'int_1d': mf6.access_memory.set_int_1d,
            'float_1d': mf6.access_memory.set_float_1d,
            'int_2d': mf6.access_memory.set_int_2d,
            'float_2d': mf6.access_memory.set_float_2d,
        }

    @staticmethod
    def _get_bool(name, origin):
        """Get a boolean value.
        """
        mf6.access_memory.get_bool(name, origin)
        return mf6.shared_data.bool_scalar

    @staticmethod
    def _get_int(name, origin):
        """Get an integer scalar.
        """
        mf6.access_memory.get_int(name, origin)
        return mf6.shared_data.int_scalar

    @staticmethod
    def _get_float(name, origin):
        """Get an float scalar.
        """
        mf6.access_memory.get_float(name, origin)
        return mf6.shared_data.float_scalar

    @staticmethod
    def _get_int_1d(name, origin):
        """Get a 1d integer array.
        """
        mf6.access_memory.get_int_1d(name, origin)
        return mf6.shared_data.int_1d

    @staticmethod
    def _get_float_1d(name, origin):
        """Get a 1d float array.
        """
        mf6.access_memory.get_float_1d(name, origin)
        return mf6.shared_data.float_1d

    @staticmethod
    def _get_int_2d(name, origin):
        """Get a 2d integer array.
        """
        mf6.access_memory.get_int_2d(name, origin)
        return mf6.shared_data.int_2d

    @staticmethod
    def _get_float_2d(name, origin):
        """Get a 2d float array.
        """
        mf6.access_memory.get_float_2d(name, origin)
        return mf6.shared_data.float_2d

    def get_value(self, name, origin):
        """Get the value for any dimension and data type.
        """
        entry = self.mf6_data_type_table[(name, origin)]
        data_type = entry['data_type']
        func = self.reading_functions[data_type]
        return func(name, origin)

    def set_value(self, name, origin, value):
        """Set the value of any dimension and data type.
        """
        entry = self.mf6_data_type_table[(name, origin)]
        data_type = entry['data_type']
        func = self.writing_functions[data_type]
        func(name, origin, value)
