# pymf6

Python Wrapper for MODFLOW 6

## Installation

Currently, the simplest way to install is to use the provided `conda` package.
You need to install
[Anaconda](https://www.anaconda.com/distribution/)
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
Once installed, add two channels to your config:

    conda config --add channels msys2
    conda config --add channels hydrocomputing

and install `pymf6` with:

    conda install pymf6

## Usage

`pymf6` provides two functions that live in
`pymf6.fortran_io`.

1. Get values from MODFLOW 6

   `get_value(name, origin)`

2. Set values in MODFLOW 6:

   `set_value(name, origin)`

where `name` is the name of a variable an d `orgin` is the name
of variable group  in MODFLOW 6.
You need to provide a callback, i.e. a Python callable that will be
call by MODLFOW 6 for each time step.
In order to keep state between calls a class with a special method
`__call__` seems the way to go.

This is a simple example:

    #!/usr/bin/env python

    """Simple callback test
    """

    from pymf6.fortran_io import get_value, set_value
    from pymf6 import mf6

    class Func:
        """Class whose instances act like a function, i.e. are callables
        """
        def __call__(self):
            # For each MODFLOW 6 time step
            lrch = get_value('LRCH', 'SLN_1')
            print('LRCH', lrch.shape)
            lrch[0, 4:10] = 22
            set_value('LRCH', 'SLN_1', lrch)

    if __name__ == '__main__':
        mf6.mf6_sub(Func())
