#!/usr/bin/env python

"""Simple callback test
"""


from pymf6.fortran_io import FortranValues
from pymf6 import mf6


class Func:
    # pylint: disable=too-few-public-methods
    """
    Callback
    """

    def __init__(self, stop=2, verbose=False):
        self.counter = 0
        self.stop = stop
        self.set_value = FortranValues(verbose=verbose).set_value

    def __call__(self):
        self.counter += 1
        print(f'>>> Python: Called {self.counter} times')
        if self.counter >= self.stop:
            print(f'Stopping from Python after {self.stop} time steps.')
            self.set_value('ENDOFSIMULATION', 'TDIS', True)


if __name__ == '__main__':
    mf6.mf6_sub(Func(verbose=True))
