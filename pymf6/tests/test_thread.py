#!/usr/bin/env python

"""Simple callback test in a thread
"""

from queue import Queue
from threading import Thread
import time

import numpy as np

from pymf6.callback import Func
from pymf6 import mf6


class MyFunc(Func):
    # pylint: disable=too-few-public-methods
    """
    Callback
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.wait = True

    def __call__(self):
        super().__call__()
        print(f'>>> Python: Called {self.counter} time')
        if self.wait:
            self.out_queue.put('next')
            self.in_queue.get()


class MF6Threaded(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.cback = MyFunc()

    def run(self):
        self.mf6 = mf6.mf6_sub(self.cback)


def main():
    mf6_threaded = MF6Threaded()
    mf6_threaded.start()
    mf6 = mf6_threaded.cback
    print('1 *** NPER', mf6.get_value('NPER', 'TDIS'))
    mf6.in_queue.put('next')
    mf6.out_queue.get()
    print('2 *** NPER', mf6.get_value('NPER', 'TDIS'))
    mf6.in_queue.put('next')
    mf6.wait = False
    mf6_threaded.join()



if __name__ == '__main__':
    main()

