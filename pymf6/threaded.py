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
        self._in_queue = Queue()
        self._out_queue = Queue()
        self._wait = True

    def __call__(self):
        super().__call__()
        if self._wait:
            self._out_queue.put('next')
            self._in_queue.get()


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
        # Shorten the names for interactive use.
        self.names = self.mf6.names
        self.show_all_names = self.mf6.show_all_names
        self.get_value = self.mf6.get_value
        self.set_value = self.mf6.set_value
        self.simulation = self.mf6.simulation
        self.simulation.init_after_first_call()

    def next_step(self):
        """
        Do next MF6 time step.
        """
        #  pylint: disable=protected-access
        self.mf6._in_queue.put('next')
        self.mf6._out_queue.get()

    def run_to_end(self):
        """
        Do next MF6 time step and run to end of simulation without
        further interactions.
        """
        #  pylint: disable=protected-access
        self.mf6._in_queue.put('next')
        self.mf6._wait = False
        self._mf6_threaded.join()
