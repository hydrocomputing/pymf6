# Change to directory `examples/ex16-mfnwt2` before running this script.

"""Example program that shows some temporal information from MF6.
"""

from pymf6.callback import Func
from pymf6 import mf6


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    # PyLint cannot understand MF6 variable access such as
    # `self.simulation.TDIS`
    # pylint: disable=no-member

    def __init__(self):
        super().__init__()
        # First model. There is only one.
        self.model = self.simulation.models[0]
        # First simulation. There is only one.
        self.sim = self.simulation.solution_groups[0]

    def __call__(self):
        """
        Override the `__call__´ from `Func`.

        :return: None
        """
        super().__call__()
        # If the in stress period 3
        if self.simulation.TDIS.KPER.value == 3:
            # set all constant head boundary conditions to 10
            self.model.CHD_1.BOUND[:] = 10
            # Change ths values to see how the calculated water level changes.
        else:
            # other set them to 25.
            self.model.CHD_1.BOUND[:] = 25
        # Show the mean water level to see changes of modifying CHD_1.
        print(self.sim.X.value.mean())


if __name__ == '__main__':
    # pylint: disable=c-extension-no-member
    mf6.mf6_sub(MyFunc())
