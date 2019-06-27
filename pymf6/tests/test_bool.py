#!/usr/bin/env python

"""Simple callback test
"""

import os
import sys

import numpy as np

from pymf6.fortran_io import set_value
from pymf6 import mf6


sys.path.insert(0, os.getcwd())


class Func:
    # pylint: disable=too-few-public-methods
    """
    Callback
    """

    def __init__(self, stop=2):
        self.counter = 0
        self.stop = stop

    def __call__(self):
        self.counter += 1
        print(f'>>> Python: Called {self.counter} times')
        if self.counter >= self.stop:
            print('Stopping from Python after {self.stop} time steps.')
            set_value('ENDOFSIMULATION', 'TDIS', True)

if __name__ == '__main__':
    mf6.mf6_sub(Func())
