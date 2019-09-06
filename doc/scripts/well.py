"""Example program that synchronizes an extraction and an injection well.
"""

from contextlib import redirect_stdout

from pymf6.callback import Func
from pymf6 import mf6


class Well:
    """
    A pumping well.

    Can be used of extraction or injection.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, simulation, model, index, pumping_capacity):
        # pylint: disable=too-many-arguments
        self.name = name
        self.simulation = simulation
        self.model = model
        self.index = index
        self.pumping_capacity = pumping_capacity
        self.node_index = None
        self.current_stress_period = 0

    @property
    def water_level(self):
        """Water level at well."""
        if not self.node_index:
            self.node_index = self.model.WEL.NODELIST.value[self.index]
        return self.simulation.X.value[self.node_index]

    @property
    def pumping_rate(self):
        """Current well pumping rate."""
        return self.model.WEL.BOUND.value[0, self.index]

    @pumping_rate.setter
    def pumping_rate(self, value):
        """Set new pumping rate."""
        self.model.WEL.BOUND.value[0, self.index] = value

    def adjust_pumping_rate(self, change_value):
        """Adjust pumping rate with `change_value`.

        Make sure that the pumping capacity is not exceeded.
        Make sure it works for negative rates too.
        """
        new_potential_rate = self.pumping_rate + change_value
        if self.pumping_capacity < 0:
            new_potential_rate = min(new_potential_rate, 0)
            new_rate = max(self.pumping_capacity, new_potential_rate)
        elif self.pumping_capacity >= 0:
            new_potential_rate = max(new_potential_rate, 0)
            new_rate = min(self.pumping_capacity, new_potential_rate)
        self.pumping_rate = new_rate


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    # PyLint cannot understand MF6 variable access such as
    # `self.simulation.TDIS`
    # pylint: disable=no-member, too-many-instance-attributes

    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.model = self.simulation.models[0]
        self.sim = self.simulation.solution_groups[0]
        self.target_water_level = 16
        self.decrement = -15
        self.increment = 7
        self.withdrawal_well = Well(
            name='withdrawal',
            simulation=self.sim,
            model=self.model,
            index=1,
            pumping_capacity=-300)
        self.infiltration_well = Well(
            name='infiltration',
            simulation=self.sim,
            model=self.model,
            index=0,
            pumping_capacity=-self.withdrawal_well.pumping_capacity)
        if self.verbose:
            print('      {:>10s} {:>6s} {:>10s} {:>6s}'.format(
                'withdrawal', 'rate', 'infil.', 'rate'))

    @property
    def current_stress_period(self):
        """The current stress period."""
        return self.simulation.TDIS.KPER.value

    def __call__(self):
        """
        Override the `__call__´ from `Func`.

        :return: None
        """
        super().__call__()
        self.withdrawal_well.current_stress_period = self.current_stress_period
        if self.current_stress_period > 1:
            if self.withdrawal_well.water_level <= self.target_water_level:
                self.withdrawal_well.adjust_pumping_rate(self.increment)
            elif self.withdrawal_well.water_level > self.target_water_level:
                self.withdrawal_well.adjust_pumping_rate(self.decrement)
            self.infiltration_well.pumping_rate = -self.withdrawal_well.pumping_rate
            self.withdrawal_well.pumping_rate = self.withdrawal_well.pumping_rate
            withd = self.withdrawal_well
            infil = self.infiltration_well
            if self.verbose:
                print(f'      {withd.water_level:10.2f} {withd.pumping_rate:6.2f}',
                      f'{infil.water_level:10.2f} {infil.pumping_rate:6.2f}')


if __name__ == '__main__':
    # pylint: disable=c-extension-no-member
    def main(screen_file='screen.txt'):
        """
        Sample run with redirected `print`.
        :param screen_file: File name for printed output.
        :return: None
        """
        with open(screen_file, 'w') as screen, redirect_stdout(screen):
            mf6.mf6_sub(MyFunc(verbose=True))
    main()
