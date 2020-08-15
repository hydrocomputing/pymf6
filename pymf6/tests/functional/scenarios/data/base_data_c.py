"""Data for the base model
"""

from copy import deepcopy

from .base_data_a import data

data = deepcopy(data)


data['chd'] = {
    'stress_periods':[
        {'h_west': -3, 'h_east': -6},
            ]
        }


data['wel'] = {
    'abs': {
        'name': 'Abstraction Well',
        'coords': (1, 49, 100),
        'rates': [0, 0, 0]
        },
    }

data['riv'] = {
    'name': 'sewer_pipe',
    'layer': 0,
    'row': 50,
    'columns': range(190, 209),
    'cond': 10 / 86400,
    'rbot': -2,
    'stage': -2,
    'kper': 2,
    }
