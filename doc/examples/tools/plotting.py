"""Plot model results.
"""

from matplotlib import pyplot as plt
import numpy as np
import flopy
from flopy.utils.postprocessing import get_specific_discharge

from make_model import get_simulation


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


def show_well_head(
        model_data,
        y_start=0.3,
        y_end=1.05,
        tolerance=0.01,
        head_limit=0.5,
        x=(0, 32)):
    """Plot head at well over time."""
    sim = get_simulation(model_data['model_path'], model_data['name'])
    gwf = sim.get_model(model_data['name'])
    heads = gwf.output.head().get_ts(model_data['wel_coords'])
    _, ax = plt.subplots()
    ax.plot(heads[:, 0], heads[:, 1], label='Well water level')
    ax.set_xlabel('Time (d)')
    ax.set_ylabel('Water level (m)')
    y_start = y_start
    y_end = y_end
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
    y1 = [head_limit - tolerance, head_limit - tolerance]
    y2 = [head_limit + tolerance, head_limit + tolerance]
    ax.plot(x, y1, color='red', linestyle=':',
            label='Target water level range')
    ax.plot(x, y2, color='red', linestyle=':')
    ax.plot(
         x_stress_1, y_stress,
         color='lightblue', linestyle=':', label='Stress periods')
    ax.plot(
         *x_stresses,
         color='lightblue', linestyle=':')
    ax.legend(loc=(1.1, 0))
    return ax
