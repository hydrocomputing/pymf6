"""Test sceanrio A (see Excel file `pymf6_MF6_benchmarks.xlsx`)
"""

from copy import deepcopy
from pprint import pprint

from frozendict import frozendict

from pymf6.callback import Func
from pymf6.tests.functional.test_builder.runners import (
    mf6_pure, mf6_pymf6, show_diff, calc_errors, run_parameter_sweep,
    make_error_stats)

from data.base_data_c import data as base_data_c

class MyFunc(Func):
    """Class whose instances act like a function, i.e. are callables
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
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
            self.riv_stage_changed = True
            self.model.WEL_0.BOUND[0][0][0] = self.data['wel']['abs']['rates'][2]
            self.model.RIV_0.BOUND[0][0][:] = self.data['riv']['stage']


class Empty:  # pylint: disable-msg=too-few-public-methods
    """Do nothing
    """



def main():
    """Run all models
    """

    rates = {
        'abs': round(-100/86400, 6),
        }
    stage = -1

    wel_data = deepcopy(base_data_c['wel'])
    wel_data['abs']['rates'] = [0, 0, rates['abs']]
    riv_data = deepcopy(base_data_c['riv'])
    riv_data['stage'] = stage
    data = {'wel': wel_data, 'riv': riv_data}

    mf6_pure('c_base', base_data=base_data_c)
    mf6_pure(model_name='c_mf6_pure', base_data=base_data_c, data=data)
    mf6_pymf6(model_name='c_pymf6_base', data=base_data_c, cb_cls=Empty)
    mf6_pymf6(
        model_name='c_pymf6_riv', data=base_data_c, cb_cls=MyFunc,
        kwargs={'stage': stage, 'rates': frozendict(rates)})

    show_diff('c_base', 'c_mf6_pure')
    show_diff('c_mf6_pure', 'c_pymf6_riv')
    pprint(calc_errors('c_mf6_pure', 'c_pymf6_riv'))
    show_diff('c_base', 'c_pymf6_base')
    pprint(calc_errors('c_base', 'c_pymf6_base'))
    show_diff('c_base', 'c_pymf6_riv')


def run_scenario_c(key, rates=None, stage=None, data=None, new_base_data=None):
    """Scenario C specific
    """

    if rates:
        wel_data = deepcopy(base_data_c['wel'])
        wel_data['abs']['rates'] = [0, 0, rates['abs']]
        riv_data = deepcopy(base_data_c['riv'])
        riv_data['stage'] = stage
        wel_river = {'wel': wel_data, 'riv': riv_data}
        if data:
            data.update(wel_river)
        else:
            data = wel_river

    run_parameter_sweep(
        key, MyFunc, data, scenario_name='c',
        base_data=base_data_c,
        new_base_data=new_base_data)


def run_all():
    """Run all calculations
    """
    run_scenario_c(
        key='-100-1',
        rates={
        'abs': round(-100/86400, 6),
        },
        stage=-1
    )
    run_scenario_c(
        key='-200-1',
        rates={
        'abs': round(-200/86400, 6),
        },
        stage=-1
    )

    data={
        'riv':{
            'name': 'sewer_pipe',
            'layer': 0,
            'row': 50,
            'columns': range(180, 199),
            'cond': round(10 / 86400, 6),
            'rbot': -2,
            'stage': -2,
            'kper': 2,
            }
        }
    run_scenario_c(
        key='-100-1coords',
        rates={
            'abs': round(-100/86400, 6),
            },
        stage=-1,
        data=data,
        new_base_data=data,
    )

def show_errors():
    """Show cumulated error statistics
    """
    pprint(make_error_stats('c'))


if __name__ == '__main__':
    # main()
    # run_all()
    show_errors()
