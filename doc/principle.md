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
Python's special method
[`__call__`](https://docs.python.org/3/reference/datamodel.html?highlight=__call__#object.__call__)
allows an instance of a class to become a callable.
By means of the `self` object, such a callable can keep state
between calls. 

This is a simple example:

    #!/usr/bin/env python

    """Simple callback test
    """

    from pymf6.callback import Func
    from pymf6 import mf6

    class MyFunc(Func):
        """Class whose instances act like a function, i.e. are callables
        """

        def __call__(self):
            super().__call__()
            print(f'>>> Python: Called {self.counter} times')
            # For each MODFLOW 6 time step
            lrch = get_value('LRCH', 'SLN_1')
            print('LRCH', lrch.shape)
            lrch[0, 4:10] = 22
            self.set_value('LRCH', 'SLN_1', lrch)

    if __name__ == '__main__':
        mf6.mf6_sub(MyFunc())

Here `self.counter` is initialized with zero at instantiation and incremented
with `super().__call__()` .


## Getting and Setting MODFLOW values

The methods:

1. `self.get_value(name, origin)`
2. `self.fortran_io.set_value(name, origin), value`

make up the core of the `pymf6` API.
They allow to access all variables exposed by the MODFLOW 6 memory manager.
The transformation of the datatype and dimension is done automatically. 

The arguments internal MODFLOW 6 descriptors:

* `name` is the internal MODFLOW 6 name of a variable
* `origin` is the internal MODFLOW 6 group of this variable

## Use of `ORIGIN` and `NAME` from `mfsim.lst`

If the `mfsin.name` file contains this option:

    BEGIN OPTIONS
      MEMORY_PRINT_OPTION ALL
    END OPTIONS
    
all `ORIGIN`/`NAME` pairs along with their datatypes and further information 
will be written to the end of `mfsim.lst`.


`pymf6` does one full MODFLOW run with this option and reads the values of
`ORIGIN` and `NAME` from `mfsim.lst`.
The results are saved in a `pickle` file.
Therefore, this pre-run needs to be done only once.
A new pre-run can be forced my deleting the pickle file `data_mapping.pkl`. 
