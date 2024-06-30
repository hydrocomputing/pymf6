"""
Create models with different discretization.

Cells with sizes of 100, 10, and 1 m.
"""

from pathlib import Path

from pymf6tools.base_model import make_model_data
from pymf6tools.make_model import get_simulation, make_input, run_simulation


BASE_MODEL_DATA = {
    'cell_width': 100,
    'cell_height': 100,
    'cell_thickness': 10,
    'model_width': 1_000,
    'model_height': 1_000,
    'q': -500,
    'chd_left': 12,
    'chd_right': 12,
}


def create_model(
    models_path=Path('models'),
    base_name='d',
    model_data=None,
    extra_model_data=None,
):
    """Create well pumping model."""
    """Create model name with discretization info."""
    if model_data is None:
        model_data = BASE_MODEL_DATA.copy()
    if extra_model_data:
        model_data.update(extra_model_data)
    cell_width = model_data['cell_width']
    cell_height = model_data['cell_height']
    cell_thickness = model_data['cell_thickness']
    model_width = model_data['model_width']
    model_height = model_data['model_height']
    q = model_data['q']
    chd_left = model_data['chd_left']
    chd_right = model_data['chd_right']

    name = f'{base_name}_{cell_width}_{cell_height}'
    model_path = models_path / name
    rows = model_width / cell_width
    cols = model_height / cell_height
    nrows = int(rows)
    ncols = int(cols)
    assert rows == nrows, f'{rows=}, {nrows=}, {model_width=}, {cell_width=}'
    assert cols == ncols
    well_col = ncols // 2
    well_row = nrows // 2
    well_layer = 0
    chd_data = [[(0, row, 0), chd_left] for row in range(nrows)]
    chd_data.extend([[(0, row, ncols - 1), chd_right] for row in range(nrows)])
    chd = {index: chd_data for index in range(2)}
    wells = {
        'well': {'q': (q, q, q), 'coords': (well_layer, well_row, well_col)}
    }

    specific_model_data = {
        'model_path': model_path,
        'name': name,
        'nrow': nrows,
        'ncol': ncols,
        'nlay': 1,
        'delr': cell_height,
        'delc': cell_width,
        'top': cell_thickness,
        'botm': 0,
        'length_units': 'm',
        'time_units': 'd',
        'times': (
            100.0,  # perlen
            100,  # nstp
            1.0,  # tsmult
        ),
        'repeat_times': 1,
        'k': [10],  # initial value of k
        'k33': [0.1],  # vertical anisotropy
        'obs': [
            ('well', (well_layer, well_row, well_col)),
        ],
        'chd': chd,
        'wells': wells,
        'transport': False,
        'river_active': False,
        'wells_active': True,
    }

    model_data = make_model_data(specific_model_data)
    make_input(model_data)
    return model_path, well_col, well_row


def run_and_get_well_level(model_path, well_col, well_row):
    """Run model and get well water level."""
    run_simulation(model_path=model_path)
    return get_well_level(model_path, well_col, well_row)


def get_well_level(model_path, well_col, well_row):
    """Get well head."""
    name = model_path.name
    sim = get_simulation(model_path, name)
    gwf = sim.get_model('gwf_' + name)
    head = gwf.output.head().get_ts((0, well_col, well_row))[-1][-1]
    return head
