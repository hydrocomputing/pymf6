"""Test sceanrio A (see Excel file `pymf6_MF6_benchmarks.xlsx`)
"""

from pprint import pprint

from frozendict import frozendict

from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff, calc_errors, run_parameter_sweep,
    make_error_stats)

from data.base_data_a import data as base_data_a


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
            chd = self.chd['stress_periods'][1]
            self.model.CHD_0.BOUND[0][0][::2] = chd['h_west']
            self.model.CHD_0.BOUND[0][0][1::2] = chd['h_east']


class Empty:  # pylint: disable-msg=too-few-public-methods
    """Do nothing
    """


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
    run_parameter_sweep(
        key, MyFunc, data, base_data=base_data_a, new_base_data=new_base_data)


def run_domain():
    """Run calculations with different domain sizes
    """
    tops = [
                (0, -10, -20),
                (-20, -30, -40),
                (-10, -20, -30)
            ]
    for x in [100, 3000, 5000]:
        for y in [100, 1000, 5000]:
            for top, upper_bot, lower_bot in tops:
                run_scenario_a(
                    key=f'x{x}_y{y}_top_{top}_upper_bot{upper_bot}_lower_bot{lower_bot}',
                    new_base_data={
                        'dis': {
                            'len_x': x,
                            'len_y': y,
                            'top': top,
                            'upper_bot': upper_bot,
                            'lower_bot': lower_bot}
                    },
                )


def run_all():
    """Run all calculations
    """
    run_domain()
    # run_scenario_a()
    # run_scenario_a(
    #     key='x100_y100',
    #     new_base_data={'dis':{'len_x': 300,'len_y': 100}},
    # )
    # run_scenario_a(
    #     key='x5000_y5000',
    #     new_base_data={'dis':{'len_x': 5000,'len_y': 5000}},
    # )


def show_errors():
    """Show cumulated error statistics
    """
    pprint(make_error_stats('a'))


if __name__ == '__main__':
    # run_base()
    # run_all()
    show_errors()
