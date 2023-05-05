"""Base model data.

Data for a basic flow model build with `flopy`.
Changing the data allows to quickly create a modified model.
Note: Not all packages are supported, yet.

Assumptions:

1. The first stress period is steady state.
2. Currently, only CHD boundary conditions are supported.
3. For all not supplied values `flopy` default values will be used.
"""


import copy


BASE_MODEL_DATA = {
    'wel_coords': (0, 4, 4),
    'wel_qs': [-0.05, -0.5, -0.05],
    #  flopy.mf6.ModflowTdis
    'times': (
        10.0,  # perlen (double) is the length of a stress period.
        120,   # nstp (integer) is the number of time steps in a stress period.
        1.0,   # tsmult (double) is the multiplier for the length of successive
               # time steps.
    ),
    'time_units': "DAYS",
    'repeat_times': 3,  # nper = repeat_times + 1
    #  flopy.mf6.ModflowGwfdis
    'nrow': 10,
    'ncol': 10,
    'nlay': 1,
    'delr': 1.0,
    'delc': 1.0,
    'top': 1.0,
    'botm': 0.0,
    #  flopy.mf6.ModflowGwfnpf
    'k': [0.5],
    'k33': [0.1],
    #  flopy.mf6.ModflowGwfsto
    'sy': 0.2,
    'ss': 0.000001,
    # flopy.mf6.ModflowGwfchd(
    'chd': [
        [(0, 0, 0), 1.],
        [(0, 9, 9), 1.]
    ],
}


def make_model_data(specific_model_data, base_model_data=BASE_MODEL_DATA):
    """Make model data.

    specific_model_data - dictionary with data specific for the current model
                          will merged with `base_model_data`
                          existing keys in `base_model_data` will be overridden
    base_model_data - dictionary with basic model data defaults to
                      `BASE_MODEL_DATA`
    """
    model_data = copy.deepcopy(base_model_data)
    model_data.update(specific_model_data)
    return model_data
