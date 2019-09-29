# Changelog


## Version 0.4.2

* Fix time of calling `cback` in `mf6sub.f90`
* Change compilation mode due to new xcode version
* Add full source of MF6 and compile all Fortran files
  (needed) for new compilation mode

## Version 0.4.1

Skipped for organizational PyPi-related reasons


## Version 0.4.0

* Add higher-level data structures for `Simulation`, `Model`, `Package` and
  `Variable` that represents MF6 data
* Add new example scripts, using this new data structures
* Add threaded, interactive API
* Update documentation


## Version 0.3.1

* Add Sphinx and markdown documentation
* Upload to readthedocs https://pymf6.readthedocs.io/en/latest/index.html

## Version 0.3.0

* Add automatic setting of option `MEMORY_PRINT_OPTION ALL`
* Add callback base class

## Version 0.2.1

* Add read and write of `bool` datatype
* Limit first MF6 run to get `name` and `origin` to one time step

## Version 0.2.0

* Add parsing of `name` and `origin` from MODFLOW 6 output
* Add basic documentation

## Version 0.1.0

* First working release
