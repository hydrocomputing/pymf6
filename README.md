# pymf6

## High-Level Python Interface for MODFLOW 6

`pymf6` can access MODFLOW variables at run time.
This allows a user to access and modify nearly all model data during a run.
A typical use case is to change values of boundary conditions based on the
current model state.
With some basic Python programming, many different problems that may be to
difficult to represent with crafting input data in a appropriate manner,
may be solved with `pymf6`.
Example usage include:

* dependent boundary conditions, i.e. the value of one boundary cell depends
  on the value of other model cells, that are calculated during the model run
* "technical" boundary conditions such as coupled extraction and injections
  wells, where the level of the extraction well should not drop under a given
  value and the injection rate should be the extractions rate, that in turn
  is a result of running model
* coupling with other models such reactive transport, unsaturated zone models,
  or sewage pipe models

## Usage Requirements

In order to use `pymf6` you need to

* understand the MODFLOW 6 variables as defined in the input files
* have a working knowledge of Python programming

## Installation

`pymf6` is a Python package.
There are two ways to install `pymf6`:

1. As a conda package from the
   [hydrocmputing channel](https://anaconda.org/hydrocomputing/pymf6)
2. As a standard Python package from [PyPi](https://pypi.org/project/pymf6/)

The installation via conda is recommended to get the lastest version.
This due to newer version of dependencies made available via
the [hydrocmputing channel](https://anaconda.org/hydrocomputing/pymf6).
There are different ways to install conda packages.
We recommend using [Pixi](https://pixi.sh/latest/).

### Alternative 1: Using Pixi

#### Installing Pixi

Please follow the instructions how to
[install Pixi](https://pixi.sh/latest/installation/).
After installing Pixi, the command `pixi` should be available in a
terminal window.

#### Creating a Pixi workspace

You need to create a Pixi workspace.
This can be done either by typing in a terminal window:

```shell
pixi init pymf6_project
cd pymf6_project
```

Now the directory `pymf6_project` contains a file named `pixi.toml` that
contains the configuration.
You need to add the channel `hydrocomputing` to your Pixi workspace.
This can be done either by typing in a terminal window:

```shell
pixi workspace channel add --prepend
```

or by editing the file `pixi.toml`,
modifying the key `channels` in the section `[workspace]` from:

```toml
[workspace]
channels = ["conda-forge"]
```

to:

```toml
[workspace]
channels = ["hydrocomputing", "conda-forge"]
```

#### Installing `pymf6`

Now you can install `pymf6` by typing:

```shell
pixi add pymf6
```

### Alternative 2: Using Conda with Miniforge, Miniconda, or Anaconda

Alternatives to using Pixi are
[Miniforge](https://github.com/conda-forge/miniforge),
[Miniconda](https://conda.io/miniconda.html),
or [Anaconda](https://www.continuum.io/downloads).
Miniforge is a minimal conda installer with the conda-forge channel as the
default channel.

Anaconda is a Python distribution with many Python packages.
Miniconda is a much smaller version of the Anaconda Distribution with a few
packages.
Make sure the
[Anaconda license](https://docs.anaconda.com/anaconda/licenses/)
works for you before using this option.
Otherwise, use Miniforge, or our recommendation Pixi.

After installing Miniconda or Anaconda, the command `conda` should be
available in a terminal window::

```shell
conda
usage: conda [-h] [-v] [--no-plugins] [-V] COMMAND ...

conda is a tool for managing and deploying applications, environments and packages.
```

#### Installing `pymf6`

In a terminal window type:

```shell
conda config --add channels conda-forge
conda config --add channels hydrocomputing
```

Create a `conda` environment by typing:

```shell
conda create -n pymf6_313 python=3.13
```

Answer "Yes" to the question(s) and type enter.

Next, type:

```shell
conda activate pymf6_313
```

### Alternative 3: Using Pip or uv

You can use `pip` to install `pymf6` if Pixi or any of the other conda-based
install method do not work for you.
You may get an older version of `pymf6` due to the availability of
dependencies.

Install with pip:

```shell
pip install pymf6
```

or with `uv`:

```shell
uv pip install pymf6
```

If you know how to use [uv](https://docs.astral.sh/uv/),
you can also create a Python project.
Likely, the options `--bare` or `--no-package` are useful to avoid creating
files and directory that are not needed:

```shell
uv init --bare pymf6_uv
```

or:

```shell
uv init --no-package pymf6_uv
```

### Install MODFLOW 6

You also need a working copy of MODFLOW 6.
Please download the version for your operating system from the
[USGS website](https://github.com/MODFLOW-ORG/modflow6/releases).
There are also
[nightly builds](https://github.com/MODFLOW-ORG/modflow6-nightly-build/releases)
with latest version.

## Configuration

While you can specify the path to the DLL and executable for each run,
it is highly recommended to create a configuration.
You need to create a file named `pymf6.ini` in your home directory.
You can find your home directory with different methods.
On Windows, the command:

```shell
set HOMEPATH
```

should work.

On Posix systems such as Linux and MacOSX, the command:

```shell
echo $HOME
```

should do.

The file `pymf6.ini` needs have to have this content

on Windows:

```ini
[paths]
dll_path = path\to\mf6\bin\libmf6.dll
exe_path = path\to\mf6\bin\mf6.exe
```

on Linux:

```ini
[paths]
dll_path = path/to/mf6/bin/libmf6.so
exe_path = path/to/mf6/bin/mf6
```

on MacOSX:

```ini
[paths]
dll_path = path/to/mf6/bin/libmf6.dylib
exe_path = path/to/mf6/bin/mf6
```

Replace the path `path/to/mf6/bin/` with with your absolute path to the
MODFLOW 6 directory `bin` that contains the shared library and the executable
you downloaded from the USGS website (see section "Installation" above).

## Test the Install

On the command line type:

```shell
pymf6
```

The output should look similar to this on Windows:

```shell
========================
pymf6 configuration data
========================
pymf6 version: 1.5.3
xmipy version: 1.3.1
modflowapi version: 0.3.0
ini file path: HOME/pymf6.ini
dll file path: path/to/dll/libmf6.dll
MODFLOW version: 6.7.0
MODFLOW Fortan variable documentation is available.
```

Where `<Home>` is the your absolute home path.
The output on Linux and MacOSX looks slightly different due to different path
separators and file extensions (see chapter "Configuration" above).

## Run a model

To test the install run a model with command:

```shell
pymf6 path/to/my/model/input
```

where `path/to/my/model/` is an absolute or relative path to the directory with
the MODFLOW input files, i.e. the directory that contains the file `mfsim.nam`.
For example any model in the directory `examples` that comes with MODFLOW 6
will do.

The output should look similar to this:

```shell
==============================
running path/to/my/model/input
==============================
NORMAL TERMINATION OF SIMULATION
GOOD path/to/my/model/input
==============================
```

## Documentation

Please read the [documentation](https://pymf6.readthedocs.io/en/latest/)
for more details.
