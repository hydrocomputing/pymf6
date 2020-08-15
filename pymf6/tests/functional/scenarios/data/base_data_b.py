"""Data for the base model
"""

from copy import deepcopy

from .base_data_a import data

data = deepcopy(data)

data['wel'] = {
        'abs': {
            'name': 'Abstraction Well',
            'coords': (0, 49, 100),
            'rates': [0, 0, 0]
        },
        'inj': {
            'name': 'Injection Well',
            'coords': (1, 49, 200),
            'rates': [0, 0, 0]
        },
        }
