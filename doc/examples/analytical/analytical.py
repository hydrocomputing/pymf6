"""
Analytical model creator.

Use Tim ML and TTim to create an equivalent model.
"""

import timml as tml
import ttim

from base_data import BASE_MODEL_DATA


def make_data(base_data=None, extra_data=None):
    """Create model_data."""
    if base_data is None:
        base_data = BASE_MODEL_DATA.copy()
    if extra_data is not None:
        base_data.update(extra_data)
    xy_end = base_data['model_width'] + 0.1
    data = {
        'kaq': 10,
        'xy_start': 0,
        'xy_end': xy_end,
        'Saq': [0.2],
        'well_x': xy_end // 2,
        'well_y': xy_end // 2,
        'chd_left': base_data['chd_left'],
        'chd_right': base_data['chd_right'],
        'q': -base_data['q'],
        'end_time': 100,
        'z': [base_data['cell_thickness'], 0],
        'well_radius': base_data['well_radius'],
        'well_screen_resistance': base_data['well_screen_resistance'],
        'well_caisson_radius': base_data['well_caisson_radius'],
    }
    return data


def make_steady_state_model(data, solve=True):
    """Create a TimML model."""
    steady_state_ml = tml.ModelMaq(
        kaq=data['kaq'], z=data['z'], npor=data['Saq']
    )
    tml.HeadLineSink1D(
        steady_state_ml,
        xls=data['xy_start'],
        hls=data['chd_left'],
    )
    tml.HeadLineSink1D(
        steady_state_ml, xls=data['xy_end'], hls=data['chd_right']
    )
    if solve:
        steady_state_ml.solve(silent=True)
    return steady_state_ml


def make_transitent_model(data, steady_state_ml=None, solve=True):
    """Create transient model."""
    ml = ttim.ModelMaq(
        kaq=data['kaq'],
        z=data['z'],
        Saq=data['Saq'],
        phreatictop=True,
        tmin=1e-3,
        tmax=data['end_time'],
        porll=data['Saq'],
        timmlmodel=steady_state_ml,
    )
    xy_start = data['xy_start']
    xy_end = data['xy_end']
    well_x = data['well_x']
    well_y = data['well_y']
    # upper_wall
    ttim.LeakyLineDoublet(
        ml, x1=xy_start, x2=xy_end, y1=xy_end, y2=xy_end, label='upper_wall'
    )
    # lower_wall
    ttim.LeakyLineDoublet(
        ml, x1=xy_start, x2=xy_end, y1=xy_start, y2=xy_start, label='lower_wall'
    )
    # rb_left
    ttim.HeadLineSink(
        ml,
        x1=xy_start,
        x2=xy_start,
        y1=xy_start,
        y2=xy_end,
        tsandh=[(0, 0)],
        label='rb_left',
    )
    # rb_right
    ttim.HeadLineSink(
        ml,
        x1=xy_end,
        x2=xy_end,
        y1=xy_start,
        y2=xy_end,
        tsandh=[(0, 0)],
        label='rb_right',
    )
    # well
    ttim.Well(
        ml,
        well_x,
        well_y,
        rw=data['well_radius'],
        res=data['well_screen_resistance'],
        rc=data['well_caisson_radius'],
        tsandQ=[(0, data['q'])],
        label='well',
    )
    if solve:
        ml.solve(silent=True)
    return ml


def get_well_head(model, data, x_offset=0.25):
    """Get well heads."""
    well_x = data['well_x']
    well_y = data['well_y']
    end_time = data['end_time']
    well = model.elementdict['well']
    result = {
        'head_inside_well': well.headinside(end_time)[0, 0],
        'well_cell_head': model.head(well_x, well_y, end_time)[0, 0],
        'well_offset_head': model.head(well_x + x_offset, well_y, end_time)[
            0, 0
        ],
    }
    return result


def plot_contour(model, data):
    """PLot contur at las time step."""
    xy_start = data['xy_start']
    xy_end = data['xy_end']
    model.contour(
        win=[xy_start, xy_end, xy_start, xy_end],
        ngr=40,
        t=data['end_time'],
        labels=True,
        decimals=1,
    )
