"""Create, run, and postprocess a MODFLOW 6 model with flopy.
"""

import flopy
from flopy.utils.postprocessing import get_specific_discharge
from matplotlib import pyplot as plt
import numpy as np


def _make_wel_stress_period(gwf, wel_q, wel_coords):
    """Create stress period data for the wel package."""
    period = flopy.mf6.ModflowGwfwel.stress_period_data.empty(
        gwf,
        maxbound=1,
    )
    period[0][0] = (wel_coords, wel_q)
    return period


def make_input(
    wel_q,
    wel_coords,
    model_path,
    name,
    exe_name='mf6',
    verbosity_level=0):
    """Create MODFLOW 6 input"""
    sim = flopy.mf6.MFSimulation(
        sim_name=name,
        sim_ws=model_path,
        exe_name=exe_name,
        verbosity_level=verbosity_level,
    )
    times = (10.0, 120, 1.0)
    tdis_rc = [(1.0, 1, 1.0), times, times, times]
    flopy.mf6.ModflowTdis(
        sim, pname="tdis",
        time_units="DAYS",
        nper=4,
        perioddata=tdis_rc,
    )
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name, save_flows=True)
    flopy.mf6.ModflowGwfdis(gwf, nrow=10, ncol=10)
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(
        gwf,
        save_flows=True,
        save_specific_discharge=True,
        icelltype=[0],
        k=[0.5],
        k33=[0.1],
    )
    sy = flopy.mf6.ModflowGwfsto.sy.empty(
        gwf,
        default_value=0.2
    )
    ss = flopy.mf6.ModflowGwfsto.ss.empty(
        gwf, default_value=0.000001
    )
    flopy.mf6.ModflowGwfsto(
        gwf,
        pname="sto",
        save_flows=True,
        save_specific_discharge=True,
        iconvert=1,
        ss=ss,
        sy=sy,
        transient={0: True},
        )

    stress_period_data = {
        1: _make_wel_stress_period(gwf, wel_q / 10, wel_coords)[0],
        2: _make_wel_stress_period(gwf, wel_q, wel_coords)[0],
        3: _make_wel_stress_period(gwf, wel_q / 10, wel_coords)[0]
    }
    flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=stress_period_data,
    )
    flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=[
            [(0, 0, 0), 1.],
            [(0, 9, 9), 1.]],
    )
    budget_file = name + '.bud'
    head_file = name + '.hds'
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[('HEAD', 'ALL'), ('BUDGET', 'ALL')])
    sim.write_simulation()


def get_simulation(model_path, exe_name='mf6', verbosity_level=0):
    """Get simulation for a model."""
    sim = flopy.mf6.MFSimulation.load(
        sim_ws=model_path,
        exe_name=exe_name,
        verbosity_level=verbosity_level,
    )
    return sim


def run_simulation(model_path, verbosity_level=0):
    """Run a MODFLOW 6 model"""
    sim = get_simulation(
        model_path,
        verbosity_level=verbosity_level)
    sim.run_simulation()


def show_heads(model_path, name, title='Head-Controlled Well'):
    """Plot calculated heads along with flow vector."""
    sim = get_simulation(model_path, name)
    gwf = sim.get_model(name)

    head = gwf.output.head().get_data()
    bud = gwf.output.budget()

    spdis = bud.get_data(text='DATA-SPDIS')[-1]
    qx, qy, _ = get_specific_discharge(spdis, gwf)
    pmv = flopy.plot.PlotMapView(gwf)
    pmv.plot_array(head)
    pmv.plot_grid(colors='white')
    pmv.contour_array(
        head,
        levels=np.arange(0.2, 1.0, 0.02),
    )
    plot = pmv.plot_vector(
        qx,
        qy,
        normalize=True,
        color="white")
    plot.axes.set_xlabel('x (m)')
    plot.axes.set_ylabel('y (m)')
    plot.axes.set_title(title)
    ticks = np.arange(0, 1.01, 0.1)
    cbar = plot.get_figure().colorbar(plot, ticks=ticks)
    cbar.set_label('Water level (m)')
    return plot


def show_well_head(model_path, name, wel_coords):
    """Plot head at well over time."""
    sim = get_simulation(model_path, name)
    gwf = sim.get_model(name)
    heads = gwf.output.head().get_ts(wel_coords)
    _, ax = plt.subplots()
    ax.plot(heads[:, 0], heads[:, 1], label='Well water level')
    ax.set_xlabel('Time (d)')
    ax.set_ylabel('Water level (m)')
    y_start = 0.3
    y_end = 1.05
    y_stress = (y_start, y_end)
    x_stress_1 = (1, 1)
    x_stress_2 = (11, 11)
    x_stress_3 = (21, 21)
    tolerance = 0.01
    head_limit = 0.5
    x = [0, 32]
    ax.set_xlim(*x)
    ax.set_ylim(y_start, y_end)
    y1 = [head_limit - tolerance, head_limit - tolerance]
    y2 = [head_limit + tolerance, head_limit + tolerance]
    ax.plot(x, y1, color='red', linestyle=':', label='Target water level range')
    ax.plot(x, y2, color='red', linestyle=':')
    ax.plot(
         x_stress_1, y_stress,
         color='lightblue', linestyle=':', label='Stress periods')
    ax.plot(
         x_stress_2, y_stress,
         x_stress_3, y_stress,
         color='lightblue', linestyle=':')
    ax.legend(loc=(1.1, 0))
    return ax


def do_all(model_path, name, wel_q=0, verbosity_level=0):
    """Do all steps:

    * create model input files
    * run the simulation
    * show calculated heads as map
    * show head at well over time
    """
    wel_coords = (0, 4, 4)
    make_input(
        wel_q=wel_q,
        wel_coords=wel_coords,
        model_path=model_path,
        name=name,
        verbosity_level=verbosity_level
        )
    run_simulation(
        model_path=model_path,
        verbosity_level=verbosity_level
        )
    show_heads(model_path, name)
    show_well_head(model_path, name, wel_coords)
