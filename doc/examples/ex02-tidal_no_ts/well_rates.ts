# The ATTRIBUTES block is required.
BEGIN ATTRIBUTES
  NAME well_1_rate well_2_rate well_6_rate
  METHOD stepwise
END ATTRIBUTES

BEGIN TIMESERIES
#time   well-1   well-2   well-6
0.0        0.0      0.0      0.0
1.0     -200.0      0.0   -100.0
11.0   -1800.0   -500.0   -200.0
21.0    -200.0   -400.0   -300.0
31.0       0.0   -600.0   -400.0
END TIMESERIES
