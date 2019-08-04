"""
Callback parent class
"""

from pymf6.fortran_io import FortranValues
from pymf6.datastructures import Simulation


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
        self.simulation = Simulation(fortran_values, self._mf6_data_type_table)

    def __call__(self):
        self.counter += 1
        if self.counter == 1:
            self.simulation.init_after_first_call()

    @property
    def names(self):
        """All name-group pairs"""
        return self._mf6_data_type_table.keys()

    def show_all_names(self, show_data_types=False, limit=None):
        """
        Print all name-group pairs, optionally with their types
        :param show_data_types: flag to show dat types or not
        :param limit: limit to n name, None shows all
        :return: None
        """
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
