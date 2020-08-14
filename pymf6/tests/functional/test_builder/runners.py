"""Scenario runners
"""

from copy import deepcopy

import flopy

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


def mf6_pymf6(model_name, cb_cls, data, sim_dir='.simulations'):
    """Run a MF6 mode wot `pymf6` using `cb_cls`
    """
    model = BaseModel(model_name, data)
    model.write_simulation()
    with TempDir(f'{sim_dir}/{model_name}'):
        run(cb_cls())


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
    print(f'Min diff: {diff.min()}, Max diff: {diff.max()}')
    print()
