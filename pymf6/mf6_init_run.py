"""
Script to run MF6 for one time step

This is needed in order to generate the name-origin entries.
"""


from pymf6 import mf6
from pymf6.fortran_io import FortranValues


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
            self.set_value('ENDOFSIMULATION', 'TDIS', True)


if __name__ == '__main__':
    print('start')
    mf6.mf6_sub(Func())
