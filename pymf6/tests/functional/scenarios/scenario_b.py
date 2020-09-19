"""Test sceanrio A (see Excel file `pymf6_MF6_benchmarks.xlsx`)
"""

from copy import deepcopy

from pprint import pprint

from frozendict import frozendict

from data.base_data_b import data as base_data
from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff, calc_errors)


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    def __init__(self, rates):
        super().__init__()
        self.rates = rates
        self.model = self.simulation.models[0]
        self.sim = self.simulation.solution_groups[0]
        self.wel_rate_changed = False

    def __call__(self):
        """
        Change `WEL` for stress period 3.
        """
        super().__call__()
        # pylint: disable-msg=no-member
        if (not self.wel_rate_changed and
                self.simulation.TDIS.KPER.value == 3):
            self.wel_rate_changed = True
            self.model.WEL_0.BOUND[0][0][0] = self.rates['abs']
            self.model.WEL_0.BOUND[0][0][1] = self.rates['inj']


class Empty:
    pass


def main():
    """Run all models
    """

    rates = {
        'abs': -5000/86400,
        'inj': 50/86400
        }
    wel_data = deepcopy(base_data['wel'])
    wel_data['abs']['rates'] = [0, 0, rates['abs']]
    wel_data['inj']['rates'] = [0, 0, rates['inj']]
    data = {'wel': wel_data}

    mf6_pure('b_base', base_data=base_data)
    mf6_pure(model_name='b_mf6_pure', base_data=base_data, data=data)
    mf6_pymf6(model_name='b_pymf6_base', data=base_data, cb_cls=Empty)
    mf6_pymf6(
        model_name='b_pymf6_wel', data=base_data, cb_cls=MyFunc,
        kwargs={'rates': frozendict(rates)})

    show_diff('b_base', 'b_mf6_pure')
    show_diff('b_mf6_pure', 'b_pymf6_wel')
    pprint(calc_errors('b_mf6_pure', 'b_pymf6_wel'))
    show_diff('b_base', 'b_pymf6_base')
    pprint(calc_errors('b_base', 'b_pymf6_base'))
    show_diff('b_base', 'b_pymf6_wel')


if __name__ == '__main__':
    main()
