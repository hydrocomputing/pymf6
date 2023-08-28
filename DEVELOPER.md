# Developing pymf6

This document describes how to contribute to pymf6.

## Branches

All development happens in branches.
This repository contains branches of ongoing pymf6 development.
The two main branches in this repository are:

* `main`: the state of the pymf6 repository corresponding to the last release
* `develop`: the current development version of pymf6

The `develop` branch is under active development.
The `main` branch is only updated immediately prior to each new release.
The branch `main` is protected,
i.e. can only pushed by the maintainer.

### Approach

1. Fork develop`.
2. Make your own feature branch from `develop`.
   It is recommended to use a naming scheme like `dev/<new-feature>`,
   where `<new-feature>`is the name of your feature such as `betterdocs`.
3. Merge your feature branch into your fork of `develop`.
4. Create a pull request (PR) for `develop` of this repo.

## Adding Examples

Examples are located in the directory `doc/examples`.
When adding a new example,
create a new subdirectory,
using the naming pattern `doc/examples/<example_name>/`.
Connect multiple words with underscores.
Examples are typically a combination of Python source code files and
one or more Jupyter Notebooks.
You can include a Python file into a Notebook with `%load`.

## Versioning

Version numbers are handled by setuptools.
Use git tags such as `1.0.0` for versions.
This version will be used in all relevant places such as the program and the
documentation.

## Building and Testing

Build the package with:

    python -m build


Upload to PyPi:

   python -m twine upload --repository pypi dist/*
