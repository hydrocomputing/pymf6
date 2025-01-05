"""Helpers to create a MF6 model."""

from pathlib import Path

import flopy.mf6 as fp
import matplotlib.pyplot as plt


def make_model_input(name, chd_head, h_mean):
    """Create model input."""
    ws = Path(name)
    sim = fp.MFSimulation(sim_name=name, sim_ws=ws, memory_print_option='all')
    pd = [(1, 1, 1.0)] * chd_head.shape[0]
    tdis = fp.ModflowTdis(sim, nper=len(pd), perioddata=pd)
    ims = fp.ModflowIms(
        sim, complexity='simple', outer_dvclose=1e-6, inner_dvclose=1e-6
    )
    gwf = fp.ModflowGwf(
        sim,
        modelname=name,
        print_input=True,
        save_flows=True,
    )
    dis = fp.ModflowGwfdis(
        gwf,
        nlay=2,
        nrow=1,
        ncol=1,
        delr=1.0,
        delc=1.0,
        top=360,
        botm=[220, 200],
    )
    npf = fp.ModflowGwfnpf(
        gwf,
        k=50.0,
        k33=10.0,
    )
    ic = fp.ModflowGwfic(gwf, strt=chd_head[0])
    condref = 1.0
    spd = [((0, 0, 0), h_mean, condref, 319.0)]
    riv = fp.ModflowGwfriv(
        gwf, stress_period_data=spd, pname='RIVER', print_flows=True
    )
    spd = {idx: [((1, 0, 0), h)] for idx, h in enumerate(chd_head)}
    chd = fp.ModflowGwfchd(gwf, stress_period_data=spd, print_flows=True)
    oc = fp.ModflowGwfoc(
        gwf,
        head_filerecord=f'{name}.hds',
        budget_filerecord=f'{name}.cbc',
        printrecord=[('budget', 'all')],
        saverecord=[('head', 'all'), ('budget', 'all')],
    )
    sim.write_simulation()
    return sim


def get_flux(sim, name):
    """Get flux data model output."""
    gwf = sim.get_model(name)
    bud = gwf.output.budget()
    riv = bud.get_data(text='RIV')
    flux = [float(entry['q'][0]) for entry in riv]
    return flux


def plot(flux, vmin=-0.6, vmax=0.6, cell_name='river'):
    """Plot the river flux."""
    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        layout='constrained',
        figsize=(4.5, 5),
    )
    ax.set_title(f'Flux in {cell_name} cell')
    ax.set_xlim(0, 400.0)
    ax.set_ylim(vmin, vmax)
    ax.set_xlabel('Simulation time, days')
    ax.set_ylabel('Flow tate, m$^3$/d')
    ax.axhline(0, lw=0.5, ls='-.', color='black')
    ax.plot(
        flux,
        color='black',
        lw=1.0,
        label='River flux',
    )
    ax.legend()
    return ax
