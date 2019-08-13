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

`pymf6` support interactive use in Jupyter Notebook sees
[this example](https://pymf6.readthedocs.io/en/latest/notebooks/Interactive.html)
for Notebook session.
The documentation of 
[MODFLOW6 packages](https://water.usgs.gov/water-resources/software/MODFLOW-6/mf6io_6.0.4.pdf)
is very useful to understand the meaning of the available data. 


You need to provide a callback, i.e. a Python callable that will be
call by MODLFOW 6 for each time step.
A class with a special method `__call__` allows to keep state between calls.

This is a simple example:

    #!/usr/bin/env python

    # Change to directory `examples/ex16-mfnwt2` before running this script.
    
    """Example program that shows some temporal information from MF6.
    """
    
    from pymf6.callback import Func
    from pymf6 import mf6
    
    
    class MyFunc(Func):
        """Class whose instances act like a function, i.e. are callables
        """
    
        def __init__(self):
            super().__init__()
            # First model. There is only one.
            self.model = self.simulation.models[0]
            # First simulation. There is only one.
            self.sim = self.simulation.solution_groups[0]
    
        def __call__(self):
            """
            Override the `__call__´ from `Func`.
    
            :return: None
            """
            super().__call__()
            # If the in stress period 3
            if self.simulation.TDIS.KPER.value == 3:
                # set all constant head boundary conditions to 10
                self.model.CHD_1.BOUND[:] = 10
                # Change ths values to see how the calculated water level changes.
            else:
                # other set them to 25.
                self.model.CHD_1.BOUND[:] = 25
            # Show the mean water level to see changes of modifying CHD_1.
            print(self.sim.X.value.mean())
    
    
    if __name__ == '__main__':
        mf6.mf6_sub(MyFunc())

Depending on the number of the stress period, the values of all constant head
boundary conditions are set to `10` or `25`. 