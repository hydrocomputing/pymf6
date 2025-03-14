# Basic Principles

## The class MF6

The class `MF6` is the main object provided by `pymf6`.
It represents as MODFLOW 6 model.

First, we make an instance of `MF6`, providing the full path to the nam file:

```python
from pymf6.mf6 import MF6

mf6 = MF6(sim_path='path/to/my/model/input')
```

Now, we can iterate of all MODFLOW 6 time steps:

```python
for model in mf6.model_loop():
    # model can be flow, transport, or energy transport model
    # do nothing
    pass
```

This runs the model just like MODFLOW 6 does.
This not too useful as the same result can be achieved by running
MODFLOW 6 directly.

We get a reference to the flow model:

```python
gwf = mf6.models['gwf6']
```

and make the well a mutable boundary condition:

```python
mywell = gwf.packages.mywell.as_mutable_bc()
```

and get the well coordinates:

```python
mywell_coords = mywell.nodelist[0]
```

Finally, we turn off the well in third stress period (`gwf.kper == 2`) if the
groundwater level in well cell is below 0.5 (meters).

```python
for model in mf6.model_loop():
    # do something with MODFLOW 6 variables
    if gwf.kper == 2:
        mywell_head = gwf.X[mywell_coords]
        if mywell_head <= 0.5
            mywell.q = 0
```
