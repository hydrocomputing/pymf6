# Functional Tests

## Principle

1. Create a MODFLOW6 model (base model) with a a specific boundary condition
   (BC)
2. Based on this base model create another model that changes the values of
   this BC over time (pure MF6 model)
3. Using the base model, run a `pymf6` model and programmatically modify the
   BC to create the same results  as the pure MF6 model

## Tools

Use Flopy for generation of MF6 input files and reading fo model results.

## Test Builder

* simple models
* input data in dictionary
* update dictionary with new data (modifications)
* only for regular grids
* only selected MF6 packages

### Comparison of results

Compare:

MF6 base - `pymf6` base - goal: **no** difference

MF6 base - MF6 pure - goal: difference

MF6 pure - `pymf6` - goal: **no** difference

MF6 base - `pymf6` - goal: difference


## Scenarios


### A

Base model with constant head BC left and right

### B

Scenario A plus abstraction well and injection well

### C

Scenario A plus abstraction well and loosing river

## Results


````
Scenario A

Head Difference between scenario "a_base" and "a_mf6_pure"
==========================================================
Min diff: -2.0000e+00, Max diff: 4.0000e+00

Head Difference between scenario "a_mf6_pure" and "b_pymf6"
===========================================================
Min diff: -4.0000e+00, Max diff: 2.0000e+00

Head Difference between scenario "a_base" and "a_pymf6_base"
============================================================
Min diff: 0.0000e+00, Max diff: 0.0000e+00

Head Difference between scenario "a_base" and "a_pymf6"
=======================================================
Min diff: -2.0000e+00, Max diff: 4.0000e+00



Scenario B

Head Difference between scenario "b_base" and "b_mf6_pure"
==========================================================
Min diff: -4.4809e-01, Max diff: 8.2111e+00

Head Difference between scenario "b_mf6_pure" and "b_pymf6_wel"
===============================================================
Min diff: 0.0000e+00, Max diff: 6.9914e-08

Head Difference between scenario "b_base" and "b_pymf6_base"
============================================================
Min diff: 0.0000e+00, Max diff: 0.0000e+00

Head Difference between scenario "b_base" and "b_pymf6_wel"
===========================================================
Min diff: -4.4809e-01, Max diff: 8.2111e+00


Scenario C

Head Difference between scenario "c_base" and "c_mf6_pure"
==========================================================
Min diff: -1.4671e-01, Max diff: 4.6531e+00

Head Difference between scenario "c_mf6_pure" and "c_pymf6_riv"
===============================================================
Min diff: -1.0483e-05, Max diff: 0.0000e+00

Head Difference between scenario "c_base" and "c_pymf6_base"
============================================================
Min diff: 0.0000e+00, Max diff: 0.0000e+00

Head Difference between scenario "c_base" and "c_pymf6_riv"
===========================================================
Min diff: -1.4671e-01, Max diff: 4.6531e+00
```