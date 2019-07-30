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
        self._mf6_data_type_table = fortran_values.mf6_data_type_table

    def __call__(self):
        self.counter += 1


    def show_all_names(self, show_data_types=False, limit=None):
        n_names = len(self._mf6_data_type_table)
        if limit:
            print(f'Showing {limit} names out of {n_names}.')
        else:
            print(f'Showing all {n_names} names.')
        for counter, ((name, group), data_type) in enumerate(
                self._mf6_data_type_table.items()):
            if limit and counter >= limit:
                break
            if show_data_types:
                print(name, group, data_type['data_type'])
            else:
                print(name, group)
