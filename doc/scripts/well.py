"""Example program thats shows some temporal information from MF6.
"""

from pymf6.callback import Func
from pymf6 import mf6

import sys

sys.stdout = open('screen.txt', 'w')

class Well:

    def __init__(self, name, simulation, model, index, pumping_capacity):
        self.name = name
        self.simulation = simulation
        self.model = model
        self.index = index
        self.pumping_capacity = pumping_capacity
        self.node_index = None
        self.current_stress_period = 0

    @property
    def water_level(self):
        if not self.node_index:
            self.node_index = self.model.WEL.NODELIST.value[self.index]
        return self.simulation.X.value[self.node_index]

    @property
    def pumping_rate(self):
        return self.model.WEL.BOUND.value[0, self.index]

    @pumping_rate.setter
    def pumping_rate(self, value):
        self.model.WEL.BOUND.value[0, self.index] = value



    def adjust_pumping_rate(self, change_value):
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
    # pylint: disable=no-member

    def __init__(self):
        super().__init__()
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

        print('      {:>10s} {:>7s} {:>10s} {:>7s}'.format('withdrawal', 'rate', 'infil.', 'rate'))

    @property
    def current_stress_period(self):
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
            print(f'      {self.withdrawal_well.water_level:10.2f} {self.withdrawal_well.pumping_rate:7.2f}',
                  f'{self.infiltration_well.water_level:10.2f} {self.infiltration_well.pumping_rate:7.2f}')

if __name__ == '__main__':
    # pylint: disable=c-extension-no-member
    mf6.mf6_sub(MyFunc())
