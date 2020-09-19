"""Test sceanrio A (see Excel file `'ueflow_MF6_benchmarks.xlsx)
"""

from copy import deepcopy
from pprint import pprint

from frozendict import frozendict

from data.base_data_c import data as base_data
from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff, calc_errors)


class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    def __init__(self, stage, rates):
        super().__init__()
        self.stage = stage
        self.rates = rates
        self.model = self.simulation.models[0]
        self.sim = self.simulation.solution_groups[0]
        self.riv_stage_changed = False

    def __call__(self):
        """
        Change `WEL` for stress period 3.
        """
        super().__call__()
        # pylint: disable-msg=no-member
        if (not self.riv_stage_changed  and
                self.simulation.TDIS.KPER.value == 3):
            self.riv_stage_changed  = True
            self.model.WEL_0.BOUND[0][0][0] = self.rates['abs']
            self.model.RIV_0.BOUND[0][0][:] = self.stage



def main():
    """Run all models
    """

    rates = {
        'abs': -100/86400,
        }
    stage = -1

    wel_data = deepcopy(base_data['wel'])
    wel_data['abs']['rates'] = [0, 0, rates['abs']]
    riv_data = deepcopy(base_data['riv'])
    riv_data['stage'] = stage
    data = {'wel': wel_data, 'riv': riv_data}

    mf6_pure('c_base', base_data=base_data)
    mf6_pure(model_name='c_mf6_pure', base_data=base_data, data=data)
    mf6_pymf6(model_name='c_pymf6_base', data=base_data, cb_cls=Func)
    mf6_pymf6(
        model_name='c_pymf6_riv', data=base_data, cb_cls=MyFunc,
        kwargs={'stage': stage, 'rates': frozendict(rates)})

    show_diff('c_base', 'c_mf6_pure')
    show_diff('c_mf6_pure', 'c_pymf6_riv')
    pprint(calc_errors('c_mf6_pure', 'c_pymf6_riv'))
    show_diff('c_base', 'c_pymf6_base')
    pprint(calc_errors('c_base', 'c_pymf6_base'))
    show_diff('c_base', 'c_pymf6_riv')


if __name__ == '__main__':
    main()
