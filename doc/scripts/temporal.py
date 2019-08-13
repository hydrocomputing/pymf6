# Change to directory `examples/ex02-tidal` before running this script.

"""Example program thats shows some temporal information from MF6.
"""

from pymf6.callback import Func
from pymf6 import mf6


def print_from_python(*args, **kwargs):
    """Helper to add separator lines around prints from Python.

    This helps to make clear the the printed output comes from Python
    vs. the print from the MF6 extension."""

    width = 79
    sep = '#'
    print(' From Python '.center(width, sep))
    print(*args, **kwargs)
    print(sep * width)


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    # PyLint cannot understand MF6 variable access such as
    # `self.simulation.TDIS`
    # pylint: disable=no-member

    def __init__(self, wait=True):
        super().__init__()
        self.wait = wait
        self.run_time = 0
        self.total_time_steps = None
        self.total_run_time = None
        print_from_python('Starting the simulation.')
        self.ask_user()

    def ask_user(self):
        """
        Stop and ask user do the next step or run to end.
        :return: None
        """
        if self.wait:
            msg = 'Press <ENTER> for next time step. '
            msg += 'Type "end" to run to end: '
            user_input = input(msg)
            if user_input.lower().strip() == 'end':
                self.wait = False

    def _first_step(self):
        """
        Print some temporal meta information after first time step.
        :return: None
        """
        tdis = self.simulation.TDIS
        self.total_time_steps = tdis.NSTP.value.sum()
        self.total_run_time = tdis.PERLEN.value.sum()
        print_from_python('Time unit:', self.simulation.time_unit,
                          '\nNumber of stress periods:', tdis.NPER.value,
                          '\nTotal time steps', self.total_time_steps,
                          '\nTotal run time', self.total_run_time,
                          self.simulation.time_unit,
                          '\nTOTALSIMTIME', tdis.TOTALSIMTIME.value,
                          self.simulation.time_unit)

    def __call__(self):
        """
        Override the `__call__´ from `Func`.

        :return: None
        """
        super().__call__()
        if self.counter == 1:
            self._first_step()
        self.ask_user()
        tdis = self.simulation.TDIS
        delt = dis.DELT.value
        self.run_time += delt
        print_from_python(
            f'Called {self.counter} times',
            '\nDELT', delt,
            '\nCurrent time:', self.run_time,
            '\nTOTIM', tdis.TOTIM.value,
            '\nKPER', tdis.KPER.value,
            '\nKSTP', tdis.KSTP.value
        )


if __name__ == '__main__':
    # pylint: disable=c-extension-no-member
    mf6.mf6_sub(MyFunc())
