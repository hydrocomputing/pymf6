# The ATTRIBUTES block is required.
# Number of names on NAME line indicates 
#     number of time series to be created.
# NAME must precede METHOD (or METHODS).
# Either METHOD or METHODS must be specified, but not both.
# If METHOD is specified, all time series in file
#     share the same method (either LINEAR or STEPWISE).
# IF METHODS is specified, a method is specified for each time series.
#
BEGIN ATTRIBUTES
  NAME river_stage_1 river_stage_2
  METHODS linear     stepwise  
#  METHOD linear
END ATTRIBUTES

BEGIN TIMESERIES
# time  riv_1  riv_2
   0.0   40.0   41.0
   1.0   41.0   41.5
   2.0   43.0   42.0
   3.0   45.0   42.8
   4.0   44.0   43.0
   6.0   43.0   43.1
   9.0   42.0   42.4
  11.0   41.0   41.5
  31.0   40.0   41.0
END TIMESERIES
