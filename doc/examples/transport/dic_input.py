"""
Dictionary with model's input
*constants

"""

input_constants = {"nlay": 1 }


nlay = 1  # Number of layers
nrow = 31  # Number of rows
ncol = 31  # Number of columns
delr = 900.0  # Column width ($ft$)
delc = 900.0  # Row width ($ft$)
delz = 20.0  # Layer thickness ($ft$)
top = 0.0  # Top of the model ($ft$)
prsity = 0.35  # Porosity
dum1 = 2.5  # Length of the injection period ($years$)
dum2 = 7.5  # Length of the extraction period ($years$)
k11 = 432.0  # Horizontal hydraulic conductivity ($ft/d$)
qwell = 1.0  # Volumetric injection rate ($ft^3/d$)
cwell = 100.0  # Relative concentration of injected water ($\%$)
al = 100.0  # Longitudinal dispersivity ($ft$)
trpt = 1.0  # Ratio of transverse to longitudinal dispersitivity