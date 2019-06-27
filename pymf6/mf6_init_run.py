"""
Script to run MF6 for one time step

This is needed in order to generate the name-origin entries.
"""


from pymf6 import mf6
from pymf6.fortran_io import set_value

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

    def __call__(self):
        self.counter += 1
        if self.counter >= self.stop:
            set_value('ENDOFSIMULATION', 'TDIS', True)

if __name__ == '__main__':
    mf6.mf6_sub(Func())
