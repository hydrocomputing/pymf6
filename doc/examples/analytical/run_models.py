"""Run several models with different discretization."""

import pprint
from timeit import default_timer

from create_model import create_model, run_and_get_well_level


def run_model(size=100):
    """
    Create and run on model.

    `size` is size of cell `delr` by `delr` in m, i.e. `100` menats
    cell of size `100 x 100`.
    """
    m_model = {'cell_width': size, 'cell_height': size}
    return run_and_get_well_level(*create_model(extra_model_data=m_model))


def run_models(sizes, measure_runtime=True):
    """
    Run all models of given sizes.

    Returns a dictionary
    {size:
        {
            'well_level': well water level after 100 days,
            'run_time': model run if measure_runtime is True,
        }.
    """
    result = {}
    for size in sizes:
        start = default_timer()
        well_level = run_model(size)
        run_time = default_timer() - start
        result[size] = {'well_level': well_level, 'run_time': run_time}
    return result


def main():
    """Show output of `run_models`for different sizes."""
    pprint.pprint(
        run_models(
            [
                100,
                10,
                5,
                1,
                0.5,
                0.25,
            ]
        )
    )


if __name__ == '__main__':
    main()
