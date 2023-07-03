"""Create  simple tranport model."""

from pymf6.modeling_tools.make_model import make_input
from pymf6.modeling_tools.base_model import make_model_data


def create_model(model_path, name):
    """Create tranport model."""
    chd = []
    for row in range(10):
        chd.append([(0, row, 0), 1., 10.0])  # concentration of 10 at left side 
    for row in range(10):
        chd.append([(0, row, 9), 0.5, 0.0])

    wells = {}
    for row in range(1, 9):
        wells[f'wel{row}'] =  {'q': (0, 0, 0), 'coords': (0, row, 4)}

    specific_model_data = {
        'model_path': model_path,
        'name': name,
        'transport': True,
        'times': (
            50.0,  # perlen (double) is the length of a stress period.
            120,   # nstp (integer) is the number of time steps in a stress period.
            1.0,   # tsmult (double) is the multiplier for the length of successive
                   # time steps.
        ),
        'obs': [
            ('upper_left', (0, 1, 7)),
            ('lower_right', (0, 8, 1))
        ],
        'chd': chd,
        'wells': wells,
        # 'cnc': [],
    }

    model_data = make_model_data(specific_model_data)
    del model_data['cnc']
    make_input(model_data)