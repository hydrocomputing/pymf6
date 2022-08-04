"""
Data structures representing MF6 runtime data
"""

from contextlib import redirect_stdout
from io import StringIO
from re import sub

import numpy as np

from pymf6.tools.formatters import (
    format_text_table, format_html_table, make_repr, make_repr_html)

# pylint: disable=too-few-public-methods

TIME_UNIT_NAMES = ('UNDEFINED', 'SECONDS', 'MINUTES', 'HOURS', 'DAYS', 'YEARS')
TIME_UNIT_VALUES = (None, 1, 60, 3600, 86400, 31557600)
LENGTH_UNIT_NAMES = ('UNDEFINED', 'FEET', 'METERS', 'CENTIMETERS')


class Simulation:
    """
    Simulation data with nice formatting
    """

    # pylint: disable=too-few-public-methods,no-member
    # # pylint: disable=too-many-instance-attributes

    def __init__(self, mf6, nam_file):
        self._mf6 = mf6
        sol_count, self.models_meta = read_simulation_data(nam_file)
        self.solution_groups = [Solution(number) for number in
                                (range(1, sol_count + 1))]
        self.model_names = [entry['modelname'] for entry in self.models_meta]
        self.models = [Model(name) for name in self.model_names]
        self.exchanges = {}
        self.TDIS = Package('TDIS')  # pylint: disable=invalid-name
        self._name_map_orig_internal = {}
        self._name_map_internal_original = {}
        self_raw_names = []
        self._make_names()
        self._build_object_hierarchy()

    def _make_names(self):
        with redirect_stdout(StringIO()):
            self._raw_names = self._mf6.get_input_var_names()

    def _clean_name(self, name):
        """Replace dashes and spaces with underscores amd make upper case"""
        new_name = '_'.join(name.split()).replace('-', '_').upper()
        self._name_map_orig_internal[name] = new_name
        self._name_map_internal_original[new_name] = new_name
        return new_name

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
        for full_name in self._mf6.get_input_var_names():
            # name pattern is:
            # `component_name/subcomponent_name/var_name`
            # `subcomponent_name` is optional
            # examples:
            # * `TDIS/NPER`
            # * `GWF_1/DIS/INUNIT`
            # * `SLN_1/IMSLinear/IOUT`
            component_name, *subcomponent_name, var_name = full_name.split('/')
            subcomponent_name = subcomponent_name[0] if subcomponent_name else None
            if component_name == 'TDIS':
                obj = self.TDIS
            elif component_name.startswith('SLN_'):
                obj = self._get_sol_group(component_name)
            elif component_name in self.model_names:
                obj = self._get_model(component_name)
            else:
                obj = self.exchanges.setdefault(component_name, Exchange(component_name))
            if subcomponent_name:
                self._add_package_attr(
                    obj, subcomponent_name, var_name, full_name)
            else:
                self._add_attr(obj, var_name, full_name)

        for model in self.models:
            model._init_after_build_object_hierarchy()

    def _add_attr(self, obj, var_name, full_name):
        """
        Add a `Variable` instance as attribute.
        """
        # pylint: disable=too-many-arguments
        name = self._clean_name(var_name)
        setattr(obj, name, Variable(self._mf6, name, full_name))
        obj.var_names.append(name)

    def _add_package_attr(self, obj, name, var_name, full_name):
        # pylint: disable=too-many-arguments
        """
        Add a `Package` instance as attribute.
        """
        package_name = self._clean_name(name)
        package = getattr(obj, package_name, None)
        if package is None:
            package = Package(package_name)
            setattr(obj, package_name, package)
            obj.var_names.append(package_name)
            obj.package_names.append(package_name)
        self._add_attr(package, var_name, full_name)

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
    """MF6 parent object"""
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


class Model(MF6Object):
    """
    A Model such GWF_1
    """
    def __init__(self, name):
        self.name = name
        self.var_names = []
        self.package_names = []
        self.length_unit = None
        self.shape_3d = None

    def _init_after_build_object_hierarchy(self):
        """
        Set some meta data after Fortran has finished initialization
        """
        # pylint: disable=no-member
        if hasattr(self, 'DIS'):
            length_index = self.DIS.LENUNI.value
            self.length_unit = LENGTH_UNIT_NAMES[length_index]
            self.shape_3d = self.DIS.MSHAPE.value


class Package(MF6Object):
    """
    A MF6 package
    """
    def __init__(self, name):
        self.name = name
        self.var_names = []

class Exchange(MF6Object):
    """
    A MF6 exchange
    """
    def __init__(self, name):
        self.name = name
        self.var_names = []
        self.package_names = []

class Variable(MF6Object):
    """A variable of a package"""
    def __init__(self, mf6, name, full_name):
        # pylint: disable=too-many-arguments
        self.name = name
        self._internal_name = full_name
        self._mf6 = mf6
        self._value = None

    @property
    def value(self):
        """
        Get Fortran value of current instance
        """
        self._value = self._mf6.get_value_ptr(self._internal_name)
        if self._value.ndim == 1 and self._value.size == 1:
            return self._value[0]
        return self._value

    @value.setter
    def value(self, new_value):
        """Set value to Fortran
        """
        if self._value is None:
            self.value()
        self._value[:] = new_value

    def __setitem__(self, key, value):
        fvalue = getattr(self, 'value')
        fvalue.__setitem__(key, value)
        self.value = fvalue

    def __getitem__(self, item):
        return self.value


def get_sections(nam_file):
    """Read secstion of nam file.
    """
    with open(nam_file, encoding='ascii') as fobj:
        sections = {}
        in_section = False
        for raw_line in fobj:
            line = raw_line.strip()
            if line.startswith('#'):
                continue
            upper_line = line.upper()
            if upper_line.startswith('BEGIN'):
                name = upper_line.split()[1]
                sections[name] = []
                in_section = True
                continue
            if upper_line.startswith('END'):
                in_section = False
                continue
            if in_section:
                sections[name].append(line)
    return sections


def read_simulation_data(nam_file):
    """
    Read simulation data
    :param fname: 'mfsim.name'
    :return: List of dicts with data
    """
    sections = get_sections(nam_file)
    names = ['modeltype', 'namefile', 'modelname']
    models = [dict(zip(names, line.split())) for line in sections['MODELS']]
    for model in models:
        model['modelname'] = model['modelname'].upper()
    sol_count = len(sections['SOLUTIONGROUP'])
    return sol_count, models
