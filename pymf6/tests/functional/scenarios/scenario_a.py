"""Test sceanrio A (see Excel file `pymf6_MF6_benchmarks.xlsx`)
"""

from pprint import pprint

from frozendict import frozendict

from data.base_data_a import data as base_data_a
from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff, calc_errors, run_parameter_sweep)


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    def __init__(self, data):
        super().__init__()
        self.model = self.simulation.models[0]
        self.sim = self.simulation.solution_groups[0]
        self.chd = data['chd']
        self.chd_changed = False

    def __call__(self):
        """
        Change `CHD` for stress period 2.
        """
        super().__call__()
        # pylint: disable-msg=no-member
        if not self.chd_changed and self.simulation.TDIS.KPER.value == 2:
            self.chd_changed = True
            self.model.CHD_0.BOUND[0][0][::2] = self.chd['stress_periods'][1]['h_west']
            self.model.CHD_0.BOUND[0][0][1::2] = self.chd['stress_periods'][1]['h_east']


class Empty:
    pass


def run_base():
    """Run all models
    """

    data = {'chd': {
                'stress_periods': [
                    {'h_west': 6, 'h_east': 3},
                    {'h_west': 2, 'h_east': 5},
                    ]
                }
            }
    print(frozendict(data))
    mf6_pure('a_base', base_data=base_data_a)
    mf6_pure(model_name='a_mf6_pure', base_data=base_data_a, data=data)
    mf6_pymf6(model_name='a_pymf6', data=base_data_a, cb_cls=MyFunc,
               kwargs={'data': frozendict(data)})
    mf6_pymf6(model_name='a_pymf6_base', data=base_data_a, cb_cls=Empty)

    show_diff('a_base', 'a_mf6_pure')
    show_diff('a_mf6_pure', 'a_pymf6')
    pprint(calc_errors('a_pymf6', 'a_mf6_pure'))
    show_diff('a_base', 'a_pymf6_base')
    pprint(calc_errors('a_base', 'a_pymf6_base'))
    show_diff('a_base', 'a_pymf6')



def run_scenario_a(key='base', new_base_data=None):
    """Scenario A specific
    """
    data = {'chd': {
                'stress_periods': [
                    {'h_west': 6, 'h_east': 3},
                    {'h_west': 2, 'h_east': 5},
                    ]
                }
            }
    run_parameter_sweep(key, MyFunc, data, base_data=base_data_a, new_base_data=new_base_data)


def run_all():
    run_scenario_a()
    run_scenario_a(
        key='x100_y100',
        new_base_data={'dis':{'len_x': 300,'len_y': 100}},
    )
    run_scenario_a(
        key='x5000_y5000',
        new_base_data={'dis':{'len_x': 5000,'len_y': 5000}},
    )

if __name__ == '__main__':
    # run_base()
    run_all()
