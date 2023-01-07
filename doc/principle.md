# Basic Principles

## The class MF6

The class `MF6` is the main object provided by `pymf6`.
It represents as MODFLOW 6 model.

First, we make an instance of `MF6`, providing the full path to the nam file:

```python
nam_file = 'path/to/nam/file/mymodel.nam'
mf6 = MF6(nam_file=nam_file)
```

Now, we can iterate of all MODFLOW 6 time steps:

```python
for step in mf6.steps():
    # do nothing
    pass
```

This runs the model just like MODFLOW 6 does.
This not too useful as the same result can be achieved by running
MODFLOW 6 directly.

Now, let's turn of pumping of a well if the water level drops below 11:

```python
head = mf6.vars['SLN_1/X']
wel = mf6.vars['MYMODEL/WEL_0/BOUND']
for step in mf6.steps():
    # do something with MODFLOW 6 variables
    # access head at index 10
    head_10 = head[10]
    # change wel rate to zero if water level is below 11
    if head_10 < 11:
        wel[:] = 0
```
