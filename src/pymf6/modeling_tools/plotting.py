"""Plot model results.
"""

from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import flopy
from flopy.utils.postprocessing import get_specific_discharge

from pymf6.modeling_tools. make_model import get_simulation


def show_heads(
        model_path,
        name,
        title='',
        show_grid=True,
        show_wells=True):
    """Plot calculated heads along with flow vector."""
    sim = get_simulation(model_path, name)
    gwf = sim.get_model(name)

    head = gwf.output.head().get_data(kstpkper=(119, 2))
    bud = gwf.output.budget()
    spdis = bud.get_data(text='DATA-SPDIS')[240]
    qx, qy, _ = get_specific_discharge(spdis, gwf)
    pmv = flopy.plot.PlotMapView(gwf)
    levels=np.arange(0.2, 1.4, 0.02)
    arr = pmv.plot_array(head)
    if show_grid:
        pmv.plot_grid(colors='white')
    pmv.contour_array(
        head,
        levels=levels,
    )
    if show_wells:
        pmv.plot_bc(name='wel', plotAll=True, kper=1)
    plot = pmv.plot_vector(
        qx,
        qy,
        normalize=True,
        color="white")
    plot.axes.set_xlabel('x (m)')
    plot.axes.set_ylabel('y (m)')
    plot.axes.set_title(title)
    #ticks = np.arange(0, 1.41, 0.1)
    cbar = plot.get_figure().colorbar(arr) # ticks=ticks)
    cbar.set_label('Groundwater level (m)')
    return plot


def show_bcs(
        model_path,
        name,
        title='Boundary Conditions',
        bc_names = ('chd', 'wel'),
        show_grid=True):
    """Show location of boundary conditions."""
    handles = []
    sim = get_simulation(model_path, name)
    gwf = sim.get_model(name)
    pmv = flopy.plot.PlotMapView(gwf)

    def add_bc(name, handles=handles, pmv=pmv):
        """Add a BC including legend entry"""
        name = name.upper()
        bc = pmv.plot_bc(name=name, plotAll=True, kper=1)
        color = bc.cmap.colors[-1]
        handles.append(Patch(facecolor=color, edgecolor='k', label=name))
        return bc
    for bc_name in bc_names:
        plot = add_bc(bc_name)
    if show_grid:
        pmv.plot_grid()
    plot.axes.set_title(title)
    plot.axes.legend(handles=handles, loc=(1.2, 0))
    return plot

def show_concentration(
        model_path, name,
        title='',
        show_grid=True,
        levels=None,
        kstpkper=None,
        show_wells=True,
        vmin=None,
        vmax=None,
        show_contours=True,
        show_arrows=False,):
    """Plot calculated heads along with flow vector."""
    gwtname = 'gwt_' + name
    sim = get_simulation(model_path, name)
    gwt = sim.get_model(gwtname)

    conc = gwt.output.concentration().get_data(kstpkper)
    pmv = flopy.plot.PlotMapView(gwt)
    arr = pmv.plot_array(conc, vmin=vmin, vmax=vmax)
    if show_grid:
        pmv.plot_grid(colors='white')
    if show_wells:
        flow_sim = get_simulation(model_path, name)
        gwf = flow_sim.get_model(name)
        plot = pmv.plot_bc(package=gwf.get_package('wel'), plotAll=True, kper=1)
    if show_contours:
        pmv.contour_array(
            conc,
            levels=levels,
        )
    plot.axes.set_xlabel('x (m)')
    plot.axes.set_ylabel('y (m)')
    plot.axes.set_title(title)
    cbar = arr.get_figure().colorbar(arr, ticks=levels)
    cbar.set_label('Concentration')
    if show_arrows:
        gwf = sim.get_model(name)
        bud = gwf.output.budget()
        spdis = bud.get_data(text='DATA-SPDIS')[240]
        qx, qy, _ = get_specific_discharge(spdis, gwf)
        plot = pmv.plot_vector(
            qx,
            qy,
            normalize=True,
            color="white")
    return plot


def show_well_head(
        wel_coords,
        model_data,
        title='',
        y_start=0.3,
        y_end=1.05,
        upper_head_limit=None,
        lower_head_limit=None,
        x=(0, 32)):
    """Plot head at well over time."""
    sim = get_simulation(model_data['model_path'], model_data['name'])
    gwf = sim.get_model(model_data['name'])
    print(gwf.output)
    heads = gwf.output.head().get_ts(wel_coords)
    _, ax = plt.subplots()
    ax.plot(heads[:, 0], heads[:, 1], label='Well water level')
    ax.set_xlabel('Time (d)')
    ax.set_ylabel('Groundwater level (m)')
    y_stress = (y_start, y_end)
    x_stress_1 = (1, 1)
    times = model_data['times']
    times_diff = times[0]
    x_stresses = []
    for count in range(1, len(times)):
        start = count * times_diff + 1
        x_stresses.append((start, start))
        x_stresses.append(y_stress)
    ax.set_xlim(*x)
    ax.set_ylim(y_start, y_end)
    ax.set_title(title)
    limit_range = False
    one_limit = False
    text = 'Target water level'
    if (lower_head_limit is not None) and (upper_head_limit is not None):
        limit_range = True
        text += ' range'
        y1 = [lower_head_limit] * 2
        y2 =[upper_head_limit] * 2
    elif lower_head_limit is not None:
        one_limit = True
        y1 = [lower_head_limit] * 2
    elif upper_head_limit is not None:
        one_limit = True
        y1 = [upper_head_limit] * 2
    if one_limit or limit_range:
        ax.plot(x, y1, color='red', linestyle=':',
                label=text)
    if limit_range:
        ax.plot(x, y2, color='red', linestyle=':')
    ax.plot(
         x_stress_1, y_stress,
         color='lightblue', linestyle=':', label='Stress periods')
    ax.plot(
         *x_stresses,
         color='lightblue', linestyle=':')
    ax.legend(loc=(1.1, 0))
    return ax
