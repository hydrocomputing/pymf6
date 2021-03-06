# Building and Testing

Besides Python and `numpy` you need a C and Fortran compiler.
So far only `gcc` and `gfortran` are tested.
Other C and Fortran compilers that work with `f2py` (part of NumPy) should also work
but would need some changes.
Currently, only Python 3.7 has been tested.
In general, all Python versions that are supported by `f2py` should work.
If you use Python 2.7, you might need to change the Python source accordingly.
No official Python 2 is planned, though.


## Unix (Linux and Mac OS X)

Install `gcc` and `gfortran` in a recent version via your preferred install
process.

## Windows

The easiest way is to create a new `conda` environment with `numpy` installed:

    conda create -n pymf6 python=3.7 numpy

activate it:

    conda activate pymf6

Now install `gcc` and `gfortran` for Windows:

    conda install -c msys2 m2w64-toolchain


If you get this error message:

    error: Unable to find vcvarsall.bat

you need to make MinGW32 your default C compiler on Windows.
Create a file `distutils.cfg` in  the directory `PYTHONPATH\Lib\distutils`
with this content:

    [build]
    compiler = mingw32

There are two ways of building.
Which one works depends on your compiler setup.
The full compile should work for all compliers.
The

## Full Compilation

From `<path/to/repros>/pymf6/make/` type:

    python compile_full_f2py.py

This creates the extension (`*.pyd` or `*.so`) and moved into
`<path/to/repros>/pymf6/pymf6`.


## Partial Compilation

The advantage of partial compilation is a much faster compilation step.
However, compilation has only be done for these cases:

1. Compile for a new MF6 version
2. Fix a bug in the wrapping code on the Fortran side
3. Add new functionality to Fortran wrapping code

All of these should be a relative rare tasks.
Therefore, the compilation time does not matter that much.

### Clone the Needed Repos

Currently, `pymf6` is still in its very early stages.
The process contains several manual steps that can be automated in the
future.
Furthermore, the workflow might change.
The needed changes to MODFLOW 6 are not merged yet.
In general the changes to the MODFLOW 6 Fortran source are minor and
rather "formal", i.e. no changes in functionality but just moving the
main program in to a subroutine and adding another outer calling layer.
This is needed to give `f2py` the opportunity to hand in a Python callback.


As of June 2019, the source only lives in this
[cloned repo of MODFLOW 6](https://github.com/hydrocomputing/modflow6)

You need to clone it:

    git clone https://github.com/hydrocomputing/modflow6.git

Based on this
[compile instructions](https://github.com/hydrocomputing/modflow6/blob/develop/DEVELOPER.md)

from the paths:

    <path/to/mf6repro/>modflow6/pymake

run the modflow6 pymake build script:

    python makebin.py ../src/ ../bin/mf6

Note that there is no `-mc` option.
This means that temporary files will **not** be deleted.
If this step is successful, these directories will be created:

     <path/to/repros>/modflow6/pymake/mod_temp
     <path/to/repros>/modflow6/pymake/obj_temp
     <path/to/repros>/modflow6/pymake/src_temp

Using `gfortran` on Linux requires some additional option:

    python makebin.py -ff="-fbacktrace -fPIC -O3 -funroll-loops" ../src/ ../bin/mf6


Clone the `pymf6` repo:

    git clone https://github.com/hydrocomputing/pymf6.git

The file `compile_f2py.py` assumes that the directories `mod_temp` and
`obj_temp` are located relative to the `make` directory of `pymf6`, i.e.:

    <path/to/repros>/pymf6/make/
    <path/to/repros>/modflow6/pymake/

where `<path/to/repros>` is the same path .


From `<path/to/repros>/pymf6/make/` type:

    python compile_f2py.py

This creates the extension (`*.pyd` or `*.so`) and moved into
`<path/to/repros>/pymf6/pymf6`.

**Done for the compilation part. :)**


