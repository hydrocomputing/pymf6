"""
Callback parent class
"""

from pymf6.fortran_io import FortranValues


class Func:
    # pylint: disable=too-few-public-methods
    """Class whose instances act like a function, i.e. are callables

    https://docs.python.org/3/reference/datamodel.html?highlight=__call__#object.__call__

    Called when the instance is “called” as a function; if this method is
    defined, `x(arg1, arg2, ...)` is a shorthand for
    `x.__call__(arg1, arg2, ...).`


    """

    def __init__(self, verbose=False):
        self.counter = 0
        fortran_values = FortranValues(verbose=verbose)
        self.get_value = fortran_values.get_value
        self.set_value = fortran_values.set_value

    def __call__(self):
        self.counter += 1
