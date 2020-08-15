"""Test sceanrio A (see Excel file `'ueflow_MF6_benchmarks.xlsx)
"""

from data.base_data_a import data as base_data
from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff)


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    def __init__(self):
        super().__init__()
        self.model = self.simulation.models[0]
        self.sim = self.simulation.solution_groups[0]
        self.chd_changed = False

    def __call__(self):
        """
        Change `CHD` for stress period 2.
        """
        super().__call__()
        # pylint: disable-msg=no-member
        if not self.chd_changed and self.simulation.TDIS.KPER.value == 2:
            self.chd_changed = True
            self.model.CHD_0.BOUND[0][0][::2] = 2
            self.model.CHD_0.BOUND[0][0][1::2] = 5


def main():
    """Run all models
    """
    mf6_pure('a_base', base_data=base_data)
    data = {'chd': {
                'stress_periods': [
                    {'h_west': 6, 'h_east': 3},
                    {'h_west': 2, 'h_east': 5},
                    ]
                }
            }
    mf6_pure(model_name='a_mf6_pure', base_data=base_data, data=data)
    mf6_pymf6(model_name='a_pymf6', data=base_data, cb_cls=MyFunc)
    mf6_pymf6(model_name='a_pymf6_base', data=base_data, cb_cls=Func)

    show_diff('a_base', 'a_mf6_pure')
    show_diff('a_mf6_pure', 'b_pymf6')
    show_diff('a_base', 'a_pymf6_base')
    show_diff('a_base', 'a_pymf6')


if __name__ == '__main__':
    main()
