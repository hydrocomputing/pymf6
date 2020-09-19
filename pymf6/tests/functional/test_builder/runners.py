"""Scenario runners
"""

from copy import deepcopy

import flopy
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
        model_data.update(data)
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
    predictions = read_head(prediction_name)
    targets = read_head(target_name)
    return {
        'RMSE': rmse(predictions, targets),
        'MSE': mse(predictions, targets)
    }
