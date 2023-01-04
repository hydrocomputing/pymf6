# pymf6

## High-Level Python Interface for MODFLOW 6

`pymf6` allows to access MODFLOW variables at run.
This allows a user to access and modify nearly all model data during a run.
A typical use is to change values of boundary conditions based on the current
model state.
With some basic Python programming, many different problems that may be to
difficult to represent with crafting input data in a appropriate manner, may be
solved with `pymf6`.

## Installation

Install with pip:

    pip install pymf6

Install with conda or mamba:

    conda install -c hydrocomputing pymf6

or:

    mamba install -c hydrocomputing pymf6

You need to install `xmipy` with pip afterwards:

    pip install xmipy

because currently `xmipy`  is not available as conda package.

You can also add the channel hydrocomputing permanently with:

    conda config --add channels hydrocomputing

You also need a working copy of MODFLOW 6.
Please download the version for your operating system from the
[USGS website](https://water.usgs.gov/water-resources/software/MODFLOW-6/).
You might need to compile MODFLOW 6 for Linux and MacOS.
A working installation of `gcc` and `gfortran` should do.
The MODFLOW 6 download comes with a Makefile.

## Configuration

While you can specify the path to MODFLOW 6 DLL for each run, it is
highly recommended to create a configuration.
You need to create a file named `pymf6.ini` in your home directory.
You can find your home directory with different methods.
On Windows, the command:

    set HOMEPATH

should work.

On Posix systems such Linux and MacOSX, the command:

    echo $HOME

should do.

The file `pymf6.ini` needs have to have this content

on Windows:

    [paths]
    dll_path = path\to\mf6\bin\libmf6.dll


on Linux:

    [paths]
    dll_path = path/to/mf6/bin/libmf6.so


on MacOSX:

    [paths]
    dll_path = path/to/mf6/bin/libmf6.dylib

Replace the path `path/to/mf6/bin/` with with your absolute path to the
MODFLOW 6 directory `bin` that contains the shared library you downloaded from
the USGS website (see chapter "Installation" above).

## Test the Install

On the command line run:

    pymf6

The output should look similar to this on Windows:

    pymf6 configuration data
    ========================
    pxmf6 version: 1.0.0a0
    xmipy version: 1.2.0
    ini file path: <Home>\pymf6.ini
    dll file path: <Home>\mf6.4.1\bin\libmf6.dll
    MODFLOW version: 6.4.1

Where `<Home>\` is the your absolute home path.
The output on Linux and MacOSX looks slightly different due to different path
separators and file extensions (see chapter "Configuration" above).

## Run a model

To test the install run a model with command_

    pymf6 path/to/nam/file/mymodel.nam

where `path/to/nam/file/mymodel.nam` is an absolute path to a MODFLOW nam file
that is in a directory of a working MODFLOW model.
For example any model in the directory `examples` that comes with MODFLOW 6
will do.
The output should look similar to this:

    ====================================
    running path/to/nam/file/mymodel.nam
    ====================================
        INSTANCE
        LOOP START
        GOOD path/to/nam/file/mymodel.nam
    ====================================
    ====================================
