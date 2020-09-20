"""Scenario runners
"""

from copy import deepcopy
import os
import shelve

import flopy
from frozendict import frozendict
import numpy as np

from pymf6.tools.tempdir import TempDir
from pymf6.tests.functional.test_builder.base_model import BaseModel
from pymf6 import run



def mf6_pure(model_name, base_data, data=None):
    """Run an M6 model with `flopy``

    `base_data` and `data` will be merged
    """
    model_data = deepcopy(base_data)
    if data:
        for key, value in data.items():
            model_data[key].update(value)
    model = BaseModel(model_name, data=model_data)
    model.write_simulation()
    model.run_simulation()


def mf6_pymf6(model_name, cb_cls, data, sim_dir='.simulations', kwargs=None):
    """Run a MF6 mode with `pymf6` using `cb_cls`
    """
    model = BaseModel(model_name, data)
    model.write_simulation()
    with TempDir(f'{sim_dir}/{model_name}'):
        run(cb_cls, kwargs)
    model.plot_head()


def read_head(model_name, head_file=None, sim_dir='.simulations'):
    """Read head file of given run
    """
    if head_file is None:
        head_file = f'{sim_dir}/{model_name}/{model_name}.hds'
    return flopy.utils.HeadFile(head_file).get_data()


def read_budget(model_name, budget_file=None, sim_dir='.simulations'):
    """Read head file of given run
    """
    if budget_file is None:
        budget_file = f'{sim_dir}/{model_name}/{model_name}.bud'
    bud = flopy.utils.CellBudgetFile(budget_file, precision='double')
    names = [name.decode('utf-8').strip() for name in bud.textlist]
    values = {}
    for name in names:
        data = bud.get_data(text=name)[-1]
        if isinstance(data, np.recarray):
            values[name] = data['q']
        else:
            values[name] = data
    return values


def show_diff(name1, name2):
    """Show maximun and minimum head difference between two models
    """
    diff = read_head(name1) - read_head(name2)
    header = f'Head Difference between scenario "{name1}" and "{name2}"'
    print(header)
    print('=' * len(header))
    print(f'Min diff: {diff.min():8.4e}, Max diff: {diff.max():8.4e}')
    print()


def rmse(predictions, targets):
    """Calculate RMSE: (Root mean squared error)
    """
    return np.sqrt(((predictions - targets) ** 2).mean())


def mse(predictions, targets):
    """Calculate MSE: (Mean squared error)
    """
    return ((predictions - targets) ** 2).mean()


def calc_errors(target_name, prediction_name):
    """Calculate RMSE and MSE
    """
    head_predictions = read_head(prediction_name)
    head_targets = read_head(target_name)
    res = {
        'head':
         {
             'RMSE': rmse(head_predictions, head_targets),
             'MSE': mse(head_predictions, head_targets)
             }
    }
    budget_predictions = read_budget(prediction_name)
    budget_targets = read_budget(target_name)
    assert budget_predictions.keys() == budget_targets.keys()
    for name, target_value in budget_targets.items():
        res[f'budget_{name}'] = {
            'RMSE': rmse(budget_predictions[name], target_value),
            'MSE': mse(budget_predictions[name], target_value)
             }
    return res


def run_parameter_sweep(
        key,
        callback,
        data,
        new_base_data=None,
        base_data=None,
        scenario_name='a'):
    """Run MF6 and pymf6 models with same parameters.

    Results are saved in shelve database.
    """
    model_name_mf6 = f'{scenario_name}_mf6_param'
    model_name_pymf6 = f'{scenario_name}_pymf6_param'
    if new_base_data:
        for dkey, value in new_base_data.items():
            base_data[dkey].update(value)
    mf6_pure(model_name=model_name_mf6, base_data=base_data, data=data)
    mf6_pymf6(model_name=model_name_pymf6, data=base_data, cb_cls=callback,
              kwargs=frozendict({'data': data}))
    res = {}
    res['errors'] = calc_errors(model_name_pymf6, model_name_mf6)
    res['data'] = data
    res['new_base_data'] = new_base_data
    flag = 'a' if os.path.exists(f'{scenario_name}_param.db.dat') else 'c'
    with shelve.open(f'{scenario_name}_param.db', flag) as dbase:
        dbase[key] = res


def make_error_stats(scenario_name):
    """Calculate some statistics for MSE and RSE
    """
    mse = []
    rmse = []
    with shelve.open(f'{scenario_name}_param.db') as dbase:
        for value in dbase.values():
            for entry in value['errors'].values():
                try:
                    mse.append(entry['MSE'])
                    rmse.append(entry['RMSE'])
                except IndexError:
                    pass
    def make_stats(values):
        """Calculate simple statistics
        """
        val = np.array(values)
        return {
            'mean': val.mean(),
            'min': val.min(),
            'max': val.max(),
            'std': val.std(),
            'n': val.size}

    return  {'RMSE': make_stats(rmse), 'MSE': make_stats(mse)}
