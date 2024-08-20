"""Run MF6 model with control and alnalytic well."""

from contextlib import redirect_stdout
from functools import partial
from os import devnull
import warnings
import sys


from pymf6.mf6 import MF6
from pymf6.api import create_mutable_bc

from analytic_well_cell import AnalyticWell

print = partial(print, file=sys.stderr)


def make_analytic_well_cells(wel, analytic_col_name='PYMF6_ANALYTIC'):
    """Create data for anayltic wells."""
    df = wel.stress_period_data.dataframe
    if wel.get_advanced_var('inamedbound')[0]:
        df['wel_name'] = [name.lower() for name in wel.get_advanced_var('boundname_idm')]
        if not df['wel_name'].is_unique:
            multiples = df[df.duplicated('wel_name')]['wel_name'].values
            indent = '\n' + ' ' * 12
            raise ValueError(f'found multiple entries for BOUNDNAMES: {indent}{indent.join(multiples)}')
    else:
        df['wel_name'] = [f'mf_wel_{n}' for n in range(len(df))]
    analytic_col = df.get(analytic_col_name.upper())
    if analytic_col is not None:
        df = df[analytic_col > 0]
        df = df.drop(analytic_col_name, axis=1)
    else:
        # no analytic wells
        return {}
    return {name: {'index': index, 'q': q} for name, q, index in zip(df['wel_name'], df['q'], df.index)}


def run_model(model_path_controlled='models/c_100_100_multi_well', analytic_well_data=None):
    """Run a test model."""
    with warnings.catch_warnings(action='ignore'), open(devnull, 'w') as fobj:
        mf6 = MF6(model_path_controlled + '/mfsim.nam', use_modflow_api=True)
        gwf = mf6.models['gwf6']
        wel = gwf.wel
        analytic_well_cells = make_analytic_well_cells(wel)
        well_levels = {name: [] for name in analytic_well_cells}
        old_totim = gwf.totim
        with redirect_stdout(fobj):
            awells = {}
            for name, well_cell_data in analytic_well_cells.items():
                if analytic_well_data:
                    well_data = analytic_well_data.get(name)
                else:
                    well_data = None
                awells[name] = AnalyticWell(
                    gwf, node_list_index=well_cell_data['index'], well_data=well_data)
            for model in mf6.model_loop():
                new_totim = model.totim
                time_diff = new_totim - old_totim
                if time_diff > 0:
                    for name, well_cell_data in analytic_well_cells.items():
                        well_levels[name].append(
                        awells[name].calc_well_head(-well_cell_data['q'], end_time=time_diff)
                        )
                    old_totim = new_totim
    return well_levels
