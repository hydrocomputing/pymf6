"""Data for the base model
"""

data = {
    'ims': {
        'complexity': 'MODERATE',
        'outer_hclose': 1e-4,
        'outer_maximum': 50,
        'inner_maximum': 200,
        'inner_hclose': 1e-5,
        },
    'time': {
        'time_units': 'seconds',
        'stress_periods':[
            {'lenght': 1, 'unit': 's'},
            {'lenght': 30, 'unit': 'd'},
            {'lenght': 180, 'unit': 'd'}
            ]
        },
    'dis': {
        'nlay': 2,
        'nrow': 100,
        'ncol': 300,
        'len_x': 3000,
        'len_y': -1000,
        'top': 0,
        'upper_bot': -10.0,
        'lower_bot': -20.0,
        'length_units': 'METERS'
        },
    'init': {
        'initial_head': 0
        },
    'npf': {
        'sat_thickness': ['variable', 'variable'],
        'k_h': [1.e-3, 1e-5],
        'k_v': [1.e-4, 1e-6]
        },
    'sto': {
        'convert': ['convertable', 'confined'],
        'ss': [1e-5, 1e-4],
        'sy': [0.2, 0.3],
        },
    'rch': {
        # in mm/a
        'recharge': 150,
    },
    'chd': {
        'stress_periods':[
            {'h_west': 6, 'h_east': 3},
            ]
        }
}
