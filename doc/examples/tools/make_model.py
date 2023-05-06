"""Create and run a MODFLOW 6 model with flopy.
"""

import flopy

import pymf6

MF6EXE = pymf6.__mf6_exe__


def make_input(
        model_data,
        exe_name=MF6EXE,
        verbosity_level=0):
    """Create MODFLOW 6 input"""
    sim = flopy.mf6.MFSimulation(
        sim_name=model_data['name'],
        sim_ws=model_data['model_path'],
        exe_name=exe_name,
        verbosity_level=verbosity_level,
    )
    times = model_data['times']
    repeat_times = model_data['repeat_times']
    tdis_rc = [(1.0, 1, 1.0)] + [times] * repeat_times
    flopy.mf6.ModflowTdis(
        sim, pname="tdis",
        time_units=model_data['time_units'],
        nper=repeat_times + 1,
        perioddata=tdis_rc,
    )
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname=model_data['name'],
        save_flows=True)
    kwargs = {name: model_data[name] for name in
              ['nrow', 'ncol', 'nlay', 'delr', 'delc', 'top', 'botm']
              }
    flopy.mf6.ModflowGwfdis(gwf, **kwargs)
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(
        gwf,
        save_flows=True,
        save_specific_discharge=True,
        icelltype=[0],
        k=model_data['k'],
        k33=model_data['k33'],
    )
    sy = flopy.mf6.ModflowGwfsto.sy.empty(
        gwf,
        default_value=model_data['sy']
    )
    ss = flopy.mf6.ModflowGwfsto.ss.empty(
        gwf, default_value=model_data['ss']
    )
    flopy.mf6.ModflowGwfsto(
        gwf,
        pname="sto",
        save_flows=True,
        save_specific_discharge=True,
        iconvert=1,
        ss=ss,
        sy=sy,
        steady_state={0: True},
        transient={index: True for index in range(1, len(times))},
        )

    stress_period_data = {}
    for index in range(len(times)):
        entry = []
        for well in model_data['wells'].values():
            entry.append((well['coords'], well['q'][index]))
        stress_period_data[index + 1] = entry

    flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=stress_period_data,
    )
    flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=model_data['chd']
    )
    budget_file = model_data['name'] + '.bud'
    head_file = model_data['name'] + '.hds'
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[('HEAD', 'ALL'), ('BUDGET', 'ALL')])
    sim.write_simulation()


def get_simulation(model_path, exe_name=MF6EXE, verbosity_level=0):
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
