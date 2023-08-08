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
    dim_kwargs = {name: model_data[name] for name in
              ['nrow', 'ncol', 'nlay', 'delr', 'delc', 'top', 'botm']
              }
    model_data['dim_kwargs'] = dim_kwargs
    flopy.mf6.ModflowGwfdis(gwf, **dim_kwargs)
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
            value = [well['coords'], well['q'][index]]
            if model_data['transport']:
                value.append(0)
            entry.append(tuple(value))
        stress_period_data[index + 1] = entry
    wel_kwargs= {}
    if model_data['transport']:
        wel_kwargs.update({
            'auxiliary': 'CONCENTRATION',
            'pname': 'WEL-1'})
    flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=stress_period_data,
        **wel_kwargs,
    )
    chd_kwargs= {}
    if model_data['transport']:
        chd_kwargs.update({
            'auxiliary': 'CONCENTRATION',
            'pname': 'CHD-1'})
    flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=model_data['chd'],
        **chd_kwargs
    )
    budget_file = model_data['name'] + '.bud'
    head_file = model_data['name'] + '.hds'
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[('HEAD', 'ALL'), ('BUDGET', 'ALL')])

    if model_data['transport']:
        make_transport_model(sim, model_data)

    sim.write_simulation()


def make_transport_model(sim, model_data):

    # Instantiating MODFLOW 6 groundwater transport package
    gwtname = 'gwt_' + model_data['name']
    gwt = flopy.mf6.MFModel(
        sim,
        model_type='gwt6',
        modelname=gwtname,
        model_nam_file=f'{gwtname}.nam'
    )
    gwt.name_file.save_flows = True

    # create iterative model solution and register the gwt model with it
    imsgwt = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",
        # outer_dvclose=hclose,
        # outer_maximum=nouter,
        under_relaxation="NONE",
        # inner_maximum=ninner,
        # inner_dvclose=hclose,
        # rcloserecord=rclose,
        linear_acceleration="BICGSTAB",
        scaling_method="NONE",
        reordering_method="NONE",
        # relaxation_factor=relax,
        filename=f'{gwtname}.ims'
    )
    sim.register_ims_package(imsgwt, [gwt.name])

    # Instantiating MODFLOW 6 transport discretization package
    flopy.mf6.ModflowGwtdis(
        gwt,
        **model_data['dim_kwargs'],
        filename=f'{gwtname}.dis'
    )

    # Instantiating MODFLOW 6 transport initial concentrations
    flopy.mf6.ModflowGwtic(
        gwt, strt=model_data['initial_concentration'], filename=f'{gwtname}.ic'
    )

    # Instantiating MODFLOW 6 transport advection package
    flopy.mf6.ModflowGwtadv(
        gwt, scheme=model_data['scheme'], filename=f'{gwtname}.adv'
    )

    # Instantiating MODFLOW 6 transport dispersion package
    long_disp = model_data['longitudinal_dispersivity']
    ratio = model_data['dispersivity_ratio']
    if long_disp != 0:
        flopy.mf6.ModflowGwtdsp(
            gwt,
            xt3d_off=True,
            alh=long_disp,
            ath1=long_disp * ratio,
            filename=f'{gwtname}.dsp'
        )

    # Instantiating MODFLOW 6 transport mass storage package (formerly "reaction" package in MT3DMS)
    flopy.mf6.ModflowGwtmst(
        gwt,
        porosity=model_data['porosity'],
        first_order_decay=False,
        decay=None,
        decay_sorbed=None,
        sorption=None,
        bulk_density=None,
        distcoef=None,
        filename=f'{gwtname}.mst'
    )

    # Instantiating MODFLOW 6 transport source-sink mixing package
    sourcerecarray = [
        ('WEL-1', 'AUX', 'CONCENTRATION'),
        ('CHD-1', 'AUX', 'CONCENTRATION')
        ]
    flopy.mf6.ModflowGwtssm(
        gwt, sources=sourcerecarray, filename=f'{gwtname}.ssm'
    )
    if 'cnc' in model_data:
        flopy.mf6.ModflowGwtcnc(
            gwt,
            stress_period_data=model_data['cnc']
        )
    # Instantiating MODFLOW 6 transport output control package
    flopy.mf6.ModflowGwtoc(
        gwt,
        budget_filerecord=f'{gwtname}.cbc',
        concentration_filerecord=f'{gwtname}.ucn',
        concentrationprintrecord=[
            ('COLUMNS', 10, 'WIDTH', 15, 'DIGITS', 6, 'GENERAL')
        ],
        saverecord=[('CONCENTRATION', 'LAST'), ('BUDGET', 'LAST')],
        printrecord=[('CONCENTRATION', 'LAST'), ('BUDGET', 'LAST')],
    )

    # Instantiate observation package (for transport)
    obs = model_data['obs']
    if obs:
        obslist = []
        for name, obs_coords in obs:
            obslist.append([name, 'concentration', obs_coords])
        obsdict = {f'{gwtname}.obs.csv': obslist}
        flopy.mf6.ModflowUtlobs(
            gwt, print_input=False, continuous=obsdict
        )

    # Instantiating MODFLOW 6 flow-transport exchange mechanism
    flopy.mf6.ModflowGwfgwt(
        sim,
        exgtype='GWF6-GWT6',
        exgmnamea=model_data['name'],
        exgmnameb=gwtname,
        filename=f'{model_data["name"]}.gwfgwt'
    )

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
