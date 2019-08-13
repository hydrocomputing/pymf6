# Basic Principles

## Callback

`pymf6` makes MODFLOW 6 a Python extension.
The whole program is a wrapped subroutine.
This subroutine takes a so-called callback function as argument.
In our case it is a Python callable.
This callback will be called in MODFLOW 6 at the beginning of each time step.
This hands control over to Python.
Since there is only one callback and many time steps, the callback needs to
save its own state.
Python's special method `__call__`
allows an instance of a class to become a callable
(see [docs](https://docs.python.org/3/reference/datamodel.html?highlight=__call__#object.__call__)
for more details).
By means of the `self` object, such a callable can keep state
between calls. 


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

Here `self.counter` is initialized with zero at instantiation and incremented
with `super().__call__()` .


## Getting MODFLOW 6 variables

`pymf6` can access all variables exposed by the MODFLOW 6 memory manager. 
The transformation of the datatype and dimension is done automatically.  
The class `pymf6.callback.Func` provides access to all MODFLOW 6 variables.
Typical usage is by inheriting from this class: 

   class MyFunc(Func): 
   
This makes several attributes available.  
In the following `self` is used as a reference to an instance of `MyFunc`.


### Meta data

`self.simulation` provides attributes such as:

* `mf6_data_type_table`
* `model_names`
* `models`
* `models_meta`
* `solution_groups`
* `time_multiplier`
* `time_unit`

Sees the
[interactive example](https://pymf6.readthedocs.io/en/latest/notebooks/Interactive.html)
for some values of these attributes.
For example, `self.simulation.time_unit` provides the time unit, which is one of

* `UNDEFINED`
* `SECONDS`
* `MINUTES`
* `HOURS`
* `DAYS`
* `YEARS`

**Note**: All internal MODFLOW 6 names are shown in upper case.
Sometimes, lower case names are converted to upper case consistency. 
File names are not converted to keep support case sensitive file system such as 
typically used in Linux and other operating systems.

### Temporal discretization

`self.simulation.TDIS` provides access to temporal discretization data as found
in the `TDIS` package. `var_names` holds all available variable names:


    >>> self.simulation.TDIS.var_names
    ['NPER',
     'ITMUNI',
     'KPER',
     'KSTP',
     'READNEWDATA',
     'ENDOFPERIOD',
     'ENDOFSIMULATION',
     'DELT',
     'PERTIM',
     'TOTIM',
     'TOTIMC',
     'DELTSAV',
     'TOTIMSAV',
     'PERTIMSAV',
     'TOTALSIMTIME',
     'PERLEN',
     'NSTP',
     'TSMULT']

For example, `self.simulation.TDIS.NPER` contains the number of stress periods.
See the MODFLOW 6 documentation for the meaning of the other variable names.

### Simulations

MODFLOW 6 supports multiple simulations.
This features can be used to solve multiple models in a picard iteration loop.
In the future, couple variable-density transport or similar problems could be
represent with approach.
As of now, all examples that come with MODFLOW 6 only have one simulation.
The simulation groups are in a list.
Use indexing to get the first, and only, element:

    sim = self.simulation.solution_groups[0]
    
Again, `var_names` contains all variable names.
Count them with:

    len(sim.var_names)

### Models

MODFLOW 6 supports multiple models.
This allows to couple multiple models.
While `pymf6` has not been tested with multiple models, it holds the models in
list and should work with two or more models.
Get th first model:

    model = mf6.simulation.models[0]

Again, `var_names` contains all variable names.
The list `model.package_names` contains all packages.
For example:


    >>> model.package_names
    ['DIS',
     'NPF',
     'XT3D',
     'GNC',
     'HFB',
     'STO',
     'IC',
     'MVR',
     'OC',
     'RCH_1',
     'CHD_1',
     'CON']
     
### Packages

Each package contains variables.
Following the same pattern, `var_names` contains all variable names.


    >>> model.DIS.var_names
    ['INUNIT',
     'IOUT',
     'NODES',
     'NODESUSER',
     'NDIM',
     'ICONDIR',
     'WRITEGRB',
     'XORIGIN',
     'YORIGIN',
     'ANGROT',
 

### Variables

Modflow 6 variables come NumPy arrays:

    >>> print(model.DIS.MSHAPE)
    
    Variable MSHAPE 
    value: WriteBackArray([14, 40, 40], dtype=int32)
    shape: (3,)
    location: TEST034_NWTP2 DIS

The `value` is a `WriteBackArray`:

    >>> model.DIS.MSHAPE.value
    
    WriteBackArray([14, 40, 40], dtype=int32)
    
   
This is a special NumPy array that writes itself back aromatically to Fortran
when modified.

Using a structured grid, some variables can be represented three dimensionally.
The bottom:

    >>> print(model.DIS.BOT)
    
    Variable BOT 
    value: WriteBackArray([65., 65. , 65. , ...,  0. ,  0. ,  0. ])
    shape: (22400,)
    location: TEST034_NWTP2 DIS

can also be retrieved a 3D array:
    
    >>> model.DIS.BOT.value_3d
    
    WriteBackArray([[[65., 65. , 65. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     ...,
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ]],
    
                    [[60. , 60. , 60. , ..., 60. , 60. , 60. ],
                     [60. , 60. , 60. , ..., 60. , 60. , 60. ],
                     [60. , 60. , 60. , ..., 60. , 60. , 60. ],
                     ...,
                     [60. , 60. , 60. , ..., 60. , 60. , 60. ],
                     [60. , 60. , 60. , ..., 60. , 60. , 60. ],
                     [60. , 60. , 60. , ..., 60. , 60. , 60. ]],
    
                    [[55. , 55. , 55. , ..., 55. , 55. , 55. ],
                     [55. , 55. , 55. , ..., 55. , 55. , 55. ],
                     [55. , 55. , 55. , ..., 55. , 55. , 55. ],
                     ...,
                     [55. , 55. , 55. , ..., 55. , 55. , 55. ],
                     [55. , 55. , 55. , ..., 55. , 55. , 55. ],
                     [55. , 55. , 55. , ..., 55. , 55. , 55. ]],
    
                    ...,
    
                    [[10. , 10. , 10. , ..., 10. , 10. , 10. ],
                     [10. , 10. , 10. , ..., 10. , 10. , 10. ],
                     [10. , 10. , 10. , ..., 10. , 10. , 10. ],
                     ...,
                     [10. , 10. , 10. , ..., 10. , 10. , 10. ],
                     [10. , 10. , 10. , ..., 10. , 10. , 10. ],
                     [10. , 10. , 10. , ..., 10. , 10. , 10. ]],
    
                    [[ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ],
                     [ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ],
                     [ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ],
                     ...,
                     [ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ],
                     [ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ],
                     [ 5. ,  5. ,  5. , ...,  5. ,  5. ,  5. ]],
    
                    [[ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ],
                     ...,
                     [ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. , ...,  0. ,  0. ,  0. ]]])
          
         
Alternatively, a lay, row, column (rlc) access, where counting start at one
works:
 
    >>> model.DIS.BOT.get_value_by_lrc(1, 1, 1)   
    65.0
        
                 
## Setting MODFLOW values

Assignment changes the value that will be written back to Fortran.
 
### Assignment to `value`

The `value` of a MODFLOW 6 variable:

    >>> model.STO.INEWTON.value
    1
    
 
can be assigned to:

    >>> model.STO.INEWTON.value = 0
    
Now it is changed and will be used by MODFLOW 6:

    >>> print(model.STO.INEWTON)
    
    Variable INEWTON 
    value: 0
    location: TEST034_NWTP2 STO
    
    



### Modification of `WriteBackArray`

Arrays can be modified.

This are first five values of `BOT`:

    >>> model.DIS.BOT.value[:5]
    WriteBackArray([65., 65., 65., 65., 65.])
    
  
Modifying the first value:
  
    >>> model.DIS.BOT.value[0] = 66.5
    
    
Has an effect on the value and MODFLOW 6 use this new value:

    >>> print(model.DIS.BOT)
    
    Variable BOT 
    value: WriteBackArray([66.5, 65. , 65. , ...,  0. ,  0. ,  0. ])
    shape: (22400,)
    location: TEST034_NWTP2 DIS

Of course, this works also in 3D-mode:

    >>> bot3d = model.DIS.BOT.value_3d
    >>> bot3d[0, 0, 2] = 70
    >>> bot3d
    WriteBackArray([[[66.5, 65. , 70. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     [65. , 65. , 65. , ..., 65. , 65. , 65. ],
                     ...,
                 
## Internal Pre-Processing

If the `mfsin.name` file contains this option:

    BEGIN OPTIONS
      MEMORY_PRINT_OPTION ALL
    END OPTIONS
    
all `ORIGIN`/`NAME` pairs along with their datatypes and further information 
will be written to the end of `mfsim.lst`.

`pymf6` does one full MODFLOW run with this option on and  reads the values of 
`ORIGIN` and `NAME` from `mfsim.lst`.

The results are saved in a `pickle` file.
Therefore, this pre-run needs to be done only once.
A new pre-run can be forced my deleting the pickle file `data_mapping.pkl`. 
