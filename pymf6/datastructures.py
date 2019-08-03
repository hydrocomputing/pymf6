"""
Data structures representing MF6 runtime data
"""

import numpy as np

from pymf6.mfnames import read_simulation_data
from pymf6.tools.formatters import (
    format_text_table, format_html_table, make_repr, make_repr_html)

# pylint: disable=too-few-public-methods


def clean_name(name):
    """Replace dashes and spaces with underscores"""
    return '_'.join(name.split()).replace('-', '_')


class Simulation:
    """
    Simulation data with nice formatting
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, fortran_values, mf6_data_type_table):
        self.fortran_values = fortran_values
        self.mf6_data_type_table = mf6_data_type_table
        self.TDIS = Package('TDIS')  # pylint: disable=invalid-name
        sol_count, self.models_meta = read_simulation_data()
        self.solution_groups = [Solution(number) for number in
                                (range(1, sol_count + 1))]
        self.model_names = [entry['modelname'] for entry in self.models_meta]
        self.models = [Model(name) for name in self.model_names]
        self._build_object_hierarchy()

    def _build_object_hierarchy(self):
        """Create object hierarchy:

        Simulation:
            TDIS
               tdis variables
            Models
               model 1
                  ID
                  ...
                  <package_name>
                      ID
                      ...
               model 2
               ...
            Simulation Groups
              SLN_1
              SLN_2
        """

        for (name, origin), value in self.mf6_data_type_table.items():
            group = origin.split()
            if len(group) == 1:
                var_name = group[0]
                if var_name == 'TDIS':
                    self._add_attr(self.TDIS, name, origin, value)
                if var_name.startswith('SLN_'):
                    self._add_attr(self._get_sol_group(var_name), name, origin,
                                   value)
                if var_name in self.model_names:
                    self._add_attr(self._get_model(var_name), name, origin,
                                   value)
            else:
                obj_name, package_name = group
                if obj_name.startswith('SLN_'):
                    self._add_package_attr(self._get_sol_group(obj_name),
                                           package_name, name, origin, value)
                if obj_name in self.model_names:
                    self._add_package_attr(self._get_model(obj_name),
                                           package_name, name, origin, value)

    def _add_attr(self, obj, name, origin, value):
        """
        Add a `Variable` instance as attribute.
        :param obj:
        :param name:
        :param origin:
        :param value:
        :return: Name
        """
        name = clean_name(name)
        setattr(obj, name,
                Variable(self.fortran_values,
                         name, origin, value['data_type']))
        obj.var_names.append(name)

    def _add_package_attr(self, obj_name, package_name, name, origin,
                          value):
        # pylint: disable=too-many-arguments
        """
        Add a `Package` instance as attribute.
        :param obj_name:
        :param package_name:
        :return: Name
        """
        package_name = clean_name(package_name)
        package = getattr(obj_name, package_name, None)
        if package is None:
            package = Package(package_name)
            setattr(obj_name, package_name, package)
            obj_name.var_names.append(package_name)
            obj_name.package_names.append(package_name)
        self._add_attr(package, name, origin, value)

    def _get_model(self, model_name):
        """
        Find `Model` instance by name
        :param model_name:
        :return: model
        """
        return self.models[self.model_names.index(model_name)]

    def _get_sol_group(self, obj_name):
        """
        Find `Solution` instance
        :param obj_name:
        :return:
        """
        return self.solution_groups[int(obj_name.split('_')[-1]) - 1]

    def __repr__(self):
        return format_text_table(self.models_meta)

    def _repr_html_(self):
        return format_html_table(self.models_meta)


class MF6Object:

    def __repr__(self):
        return make_repr(self)

    def _repr_html_(self):
        return make_repr_html(self)

    def __getitem__(self, item):
        return getattr(self, item)


class Solution(MF6Object):
    """
    A solution in the solution group
    """
    def __init__(self, number):
        self.name = number
        self.var_names = []
        self.package_names = []

    def __repr__(self):
        return make_repr(self)

    def _repr_html_(self):
        return make_repr_html(self)

class Model(MF6Object):
    """
    A Model such GWF_1
    """
    def __init__(self, name):
        self.name = name
        self.var_names = []
        self.package_names = []


class Package(MF6Object):
    """
    A MF6 package
    """
    def __init__(self, name):
        self.name = name
        self.var_names = []


class Variable(MF6Object):
    """A variable of a package"""
    def __init__(self, fortran_values, name, origin, data_type):
        self.fortran_values = fortran_values
        self.name = name
        self.origin = origin
        self.data_type = data_type
        self._arr = None

    @property
    def value(self):
        """
        Get Fortran value of current instance
        :return:
        """
        arr = self.fortran_values.get_value(self.name, self.origin)
        if arr.ndim == 0:
            return arr.reshape(1)[0]
        self._arr = arr
        return arr

    @value.setter
    def value(self, new_value):
        """Set value to Fortran
        """
        self.fortran_values.set_value(self.name, self.origin,
                                      np.array(new_value))

    def __setitem__(self, key, value):
        fvalue = getattr(self, 'value')
        fvalue.__setitem__(key, value)
        self.value = fvalue

    def __getitem__(self, item):
        return self.value

    def write_back(self):
        if self._arr is None:
            self.value
        self.value = self._arr
