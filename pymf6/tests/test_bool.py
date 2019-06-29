#!/usr/bin/env python

"""Simple callback test
"""


from pymf6.callback import Func
from pymf6 import mf6


class MyFunc(Func):
    # pylint: disable=too-few-public-methods
    """
    Callback
    """

    def __init__(self, stop=2, verbose=False):
        super().__init__(verbose=verbose)
        self.stop = stop

    def __call__(self):
        super().__call__()
        print(f'>>> Python: Called {self.counter} times')
        if self.counter >= self.stop:
            print(f'Stopping from Python after {self.stop} time steps.')
            self.set_value('ENDOFSIMULATION', 'TDIS', True)


if __name__ == '__main__':
    mf6.mf6_sub(MyFunc(verbose=True))
