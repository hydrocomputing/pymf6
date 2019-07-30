#!/usr/bin/env python

"""Callback in a thread
"""

from queue import Queue
from threading import Thread

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
        if self.wait:
            self.out_queue.put('next')
            self.in_queue.get()


class MF6Threaded(Thread):
    """A thread representing MF6"""
    def __init__(self):
        super().__init__(daemon=True)
        self.cback = MyFunc()
        self.mf6 = None

    def run(self):
        """Run the thread"""
        self.mf6 = mf6.mf6_sub(self.cback)


class MF6:
    """
    MF6 run in a thread
    """
    def __init__(self):
        """

        """
        self._mf6_threaded = MF6Threaded()
        self._mf6_threaded.start()
        self.mf6 = self._mf6_threaded.cback

    def next_step(self):
        """
        Do next MF6 time step.
        """
        self.mf6.in_queue.put('next')
        self.mf6.out_queue.get()

    def run_to_end(self):
        """
        Do next MF6 time step and run to end of simulation without
        further interactions.
        """
        self.mf6.in_queue.put('next')
        self.mf6.wait = False
        self._mf6_threaded.join()
