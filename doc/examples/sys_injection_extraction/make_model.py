"""Create, run, and postprocess a MODFLOW 6 model with flopy.
"""

import flopy
from flopy.utils.postprocessing import get_specific_discharge
from matplotlib import pyplot as plt
import numpy as np

# period of stress  of the well package within the gwf6 model
def _make_wel_stress_period(gwf, wel_qin, wel_qout, wel_coordsin, wel_coordsout):
    """Create stress period data for the wel package."""
    period = flopy.mf6.ModflowGwfwel.stress_period_data.empty(
        gwf,
        maxbound=2, #integer value specifying the maximum number of wells cells that will be specified for use during any stress period.
    )
    period[0][0] = (wel_coordsin, wel_qin) # first period only injection
    period[0][1] = (wel_coordsout, wel_qout) # second period extraction also
    return period

# entry point for the simulation - before any objects
def make_input(
    wel_qin,
    wel_qout,
    wel_coordsin,
    wel_coordsout,
    model_path,
    name,
    exe_name='mf6',
    verbosity_level=0):
    """Create MODFLOW 6 input"""
    # created to load, build and save the simulation
    sim = flopy.mf6.MFSimulation(
        sim_name=name,
        sim_ws=model_path, #working folder
        exe_name=exe_name,
        verbosity_level=verbosity_level, #standard output to be written - error messages should be included (=1)
    )
    # time discretization package
    times = (10.0, 120, 1.0)
    tdis_rc = [(1.0, 1, 1.0), times, times, times]
    flopy.mf6.ModflowTdis(
        sim, pname="tdis",
        time_units="DAYS",
        nper=4, # number of stress periods
        perioddata=tdis_rc, # [perlen(len stress period), nstp(time-steps in the stressperiod), tsmult(multiplier of of the lenght of sucessive time-steps]
    )
    #iterative model solution package
    flopy.mf6.ModflowIms(sim) # default solver - nearly linear models - confined or a single unconfined layer that is tick enough to contain the water table within a single layer
    # groundwater flow model
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name, save_flows=True)
    # spatial discretization package
    flopy.mf6.ModflowGwfdis(gwf, nrow=10, ncol=10) # number ir rows and cols since the model has only one layer
    # Initial conditions package
    flopy.mf6.ModflowGwfic(gwf) #models using steady state in the beginning won't be affected
    # node property flow package pane - default is harmonic mean
    flopy.mf6.ModflowGwfnpf(
        gwf,
        save_flows=True,
        save_specific_discharge=True,
        icelltype=[0], # 0 unconfined, -1 confined
        k=[0.5], # initial value of k
        k33=[0.1], # vertical anisotropy
    )
    # storage package specifying sy - specific yield bigger than 0 means the cell is convertible
    sy = flopy.mf6.ModflowGwfsto.sy.empty(
        gwf,
        default_value=0.2 # convertible cells
    )
    #stirage package specifying ss - specific storage
    ss = flopy.mf6.ModflowGwfsto.ss.empty(
        gwf, default_value=0.000001
    )
    # storage package
    flopy.mf6.ModflowGwfsto(
        gwf,
        pname="sto",
        save_flows=True,
        save_specific_discharge=True,
        iconvert=1, # flag for each cell that specifies whether or not a cell is convertible for the storage calculation. 0 indicates confined storage is used. >0 indicates confined storage is used when head is above cell top and a mixed formulation of unconfined and confined storage is used when head is below cell top
        ss=ss,
        sy=sy,
        transient={0: True}, # keyword to indicate that stress period IPER is transient. Transient conditions will apply until the STEADY-STATE keyword is specified in a subsequent BEGIN PERIOD block
        )
    #dictionary of boundaries Each well is defined through definition of layer (int), row (int), column (int), flux (float). The simplest form is a dictionary with a lists of boundaries for each stress period, where each list of boundaries itself is a list of boundaries. Indices of the dictionary are the numbers of the stress period
    # if the number of stress periods is larger than the dic than the last speficied will apply until the end
    stress_period_data = {
        1: _make_wel_stress_period(gwf, wel_qin=wel_qin, wel_coordsin=wel_coordsin, wel_qout=wel_qout, wel_coordsout=wel_coordsout)[0],
        2: _make_wel_stress_period(gwf, wel_qin=wel_qin, wel_coordsin=wel_coordsin, wel_qout=wel_qout, wel_coordsout=wel_coordsout)[0],
        3: _make_wel_stress_period(gwf, wel_qin=wel_qin, wel_coordsin=wel_coordsin, wel_qout=wel_qout, wel_coordsout=wel_coordsout)[0]
    }
    # defines the well package
    flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=stress_period_data,
    )
    # constant head package
    flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=[
            [(0, 0, 0), 1.], # top left cell [cell_id, head, aux, boundname]
            [(0, 9, 9), 1.]], # bottom right cell
    )
    # variable for the output control
    budget_file = name + '.bud'
    head_file = name + '.hds'
    # output control package
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


def show_heads(model_path, name):
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
    pmv.plot_vector(qx, qy, normalize=True, color="white")


def show_well_head(model_path, name, wel_coordsin, wel_coordsout):
    """Plot head at well over time."""
    sim = get_simulation(model_path, name)
    gwf = sim.get_model(name)
    heads_in = gwf.output.head().get_ts(wel_coordsin)
    heads_out = gwf.output.head().get_ts(wel_coordsout)
    _, ax = plt.subplots()
    ax.plot(heads_in[:, 0], heads_in[:, 1], heads_out[:, 0], heads_out[:, 1])

# pymf6 starting model with values as 0 to check if the pymf6 responds to the model 
def do_all(model_path, name, wel_qin=0, wel_qout=0, verbosity_level=0):
    """Do all steps:

    * create model input files
    * run the simulation
    * show calculated heads as map
    * show head at well over time
    """
    wel_coordsin = (0, 2, 2)
    wel_coordsout = (0, 6, 6)
    make_input(
        wel_qin=wel_qin,
        wel_qout=wel_qout,
        wel_coordsin=wel_coordsin,
        wel_coordsout=wel_coordsout,
        model_path=model_path,
        name=name,
        verbosity_level=verbosity_level
        )
    run_simulation(
        model_path=model_path,
        verbosity_level=verbosity_level
        )
    show_heads(model_path, name)
    show_well_head(model_path, name, wel_coordsin, wel_coordsout)
