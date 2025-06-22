"""Wrapper around XmiWrapper."""

from contextlib import redirect_stdout
import json
from io import StringIO
from pathlib import Path
from textwrap import dedent
from types import MethodType
from warnings import warn

import pandas as pd
from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError
from xmipy.utils import cd

from .api import create_mutable_bc, Simulator, States
from .datastructures import Simulation
from .tools.info import (
    get_info_data,
    show_info,
    make_info_texts,
    make_info_html,
    read_ini,
)


class SimValues:
    def __init__(self, mf6):
        self.mf6 = mf6

    def __getattr__(self, name):
        return self.mf6._get_sim_val(name)


class MF6:
    """
    Wrapper around XmiWrapper and modflowapi.

    `advance_first_step = True` progresses to the first model step with
    model time > 0. This is needed to access any internal values of BCs.
    """

    # pylint: disable=too-many-instance-attributes

    # Only one instance can be initialized but not finalized.
    # Store the active instance here to improve interactive
    # experience in Notebooks.
    old_mf6 = None
    _demo = False
    mfsim_nam = 'mfsim.nam'

    def __init__(
        self,
        sim_path,
        dll_path=None,
        use_modflow_api=True,
        advance_first_step=True,
        verbose=False,
        new_step_only=False,
        do_solution_loop=True,
        _develop=False,
    ):
        def init_mf6(sim_path):
            # Finalize if initialized instance exists.
            # This is helpful for interactive work in Notebooks.
            # Use class `MF6` nit `self.__class__` to prevent child class
            # from initializing an instance at the same time an instance of
            # the parent class is still initialized.
            if MF6.old_mf6:
                try:
                    MF6.old_mf6.finalize()
                except InputError:
                    pass
            if use_modflow_api:
                self._simulator = Simulator(
                    str(self.dll_path),
                    sim_path,
                    verbose=verbose,
                    do_solution_loop=do_solution_loop,
                    _develop=_develop,
                )
                # pylint: disable=protected-access
                self._mf6 = self._simulator._mf6
                self.api = self._simulator.api
            else:
                self._mf6 = XmiWrapper(str(self.dll_path))
                self._mf6.initialize(str(self.nam_file))
            MF6.old_mf6 = self._mf6

        self.sim_path = Path(sim_path).resolve()
        if self.sim_path.is_file():
            warn(
                '\nPlease provide the simulation path as first argument to MF6.'
                f'\nThe file name {self.mfsim_nam} will be added automatically.',
                DeprecationWarning,
            )
            self.sim_path = self.sim_path.parent
        self.do_solution_loop = do_solution_loop
        self.nam_file = self.sim_path / self.mfsim_nam
        self.advance_first_step = advance_first_step
        self.verbose = verbose
        self._mf6 = None
        self._simulator = None
        self._info_data = get_info_data()
        self.mf6_docs = None
        self.api = None
        if self._info_data['mf6_doc_path']:
            self.mf6_docs = MF6Docs(self._info_data['mf6_doc_path'])
        self._info_texts = make_info_texts(self._info_data, demo=self._demo)
        ini_data = read_ini()
        self.ini_path = ini_data['ini_path']
        self.sim_values = SimValues(self)
        self.current_model_step = None

        if dll_path is None:
            self.dll_path = ini_data['dll_path']
        else:
            self.dll_path = Path(dll_path)

        if not self.nam_file.exists():
            raise FileNotFoundError(self.nam_file)
        self.name = self.sim_path.name
        with cd(self.sim_path):
            init_mf6(str(self.nam_file.parent))
            self.__class__.is_initialized = True
            self.simulation = Simulation(
                self._mf6, self.nam_file, self.mf6_docs
            )
            self.vars = self._get_vars()
        if use_modflow_api:
            self.sol_loop = self._simulator.loop()
        else:
            self.sol_loop = None

        models = {}
        self._reverse_names = {}
        type_mapping = {
            entry['modelname'].lower(): entry['modeltype']
            for entry in self.simulation.models_meta
        }
        if use_modflow_api:
            not_found_names = set()
            for name in self.api.model_names:
                name = name.lower()
                if name not in type_mapping:
                    # TODO: Find put where these names come form.
                    not_found_names.add(name)
                    continue
                prefix = type_mapping[name]
                model = self.api.get_model(name)
                model.packages = Packages(model.package_dict)
                models.setdefault(prefix, {}).setdefault(name, model)
                self._reverse_names[name] = prefix
        if not_found_names:
            print(f'{not_found_names=}')
        self.models = models
        if not use_modflow_api:
            self.steps = self._steps(new_step_only)
        if advance_first_step:
            if use_modflow_api:
                simulation_group, state = next(self.sol_loop)
                self.current_model_step = ModelStep(
                    simulation_group=simulation_group,
                    state=state,
                    do_solution_loop=self.do_solution_loop,
                )
            else:
                for step in self.steps:
                    if step > 0:
                        break

    def model_loop(self):
        """Time step loop over all models."""
        for simulation_group, state in self.sol_loop:
            # mf6_model = sol_group.get_model()
            # model_type = self._reverse_names[mf6_model.name.lower()]
            self.current_model_step = ModelStep(
                simulation_group=simulation_group,
                state=state,
                do_solution_loop=self.do_solution_loop,
            )
            yield (self.current_model_step)
            # yield Model(mf6_model=mf6_model, state=state, type=model_type)

    def _repr_html_(self):
        """
        Make a nice HTML table.

        :param obj: Python object
        :return: HTML string
        """
        return make_info_html(self._info_texts)

    @property
    def info(self):
        """Information about versions and paths."""
        show_info(self._info_texts)

    def finalize(self):
        """Finalize the model run."""
        self._mf6.finalize()

    def do_time_step(self):
        """Do one time step."""
        self._mf6.do_time_step()

    def get_current_time(self):
        """Return current model time step."""
        return self._mf6.get_current_time()

    def get_end_time(self):
        """Return end model time step."""
        return self._mf6.get_end_time()

    def update(self):
        """Update MF6 variables."""
        return self._mf6.update()

    @property
    def version(self):
        """MF6 version."""
        return self._mf6.get_version()

    def _get_vars(self):
        """
        Get all variables in dictionary.

        TODO: Currently the Fortran types LOGICAL and STRING are not
        yet supported. Ignore them for now.
        """
        values = {}
        input_err = {}
        xmi_error = {}
        with redirect_stdout(StringIO()):
            for name in self._mf6.get_input_var_names():
                try:
                    values[name] = self._mf6.get_value_ptr(name)
                except InputError as err:
                    input_err[name] = err
                except XMIError as err:
                    xmi_error[name] = err
        return values

    def _steps(self, new_step_only=False):
        """
        Provide a generator for iterating over all time steps.

        It allows to modify MODFLOW variables for each time step.
        new_step_only -yield only at new time step

        If `new_step_only` is set to `True` each step has new value.
        Otherwise the control is gain for each outer iteration,
        resulting in getting the same time step multiple times (<= `MXITER`).
        Do **NOT** set `new_step_only` to `True` if modifying time
        series data. Modifications of values will be ignore by MODFLOW.

        Example:
        -------
            mf6 = MF6(nam_file=nam_file)
            wel = mf6.vars['<model_name>/WEL/BOUND']
            for step in mf6.steps():
                # modify MODFLOW variables here
                if step > 10 and step < 20:
                    wel[:] = -10
                else:
                    wel[:] = 0

        """
        current_time = self.get_current_time()
        end_time = self.get_end_time()
        nsol = self._mf6.get_subcomponent_count()
        sol_numbers = list(range(1, nsol + 1))
        max_iters = []
        for sol_number in sol_numbers:
            max_iters.append(self.vars[f'SLN_{sol_number}/MXITER'][0])
        while current_time < end_time:
            dt = self._mf6.get_time_step()  # pylint: disable=invalid-name
            if new_step_only:
                self._mf6.prepare_time_step(dt)
                self._mf6.do_time_step()
                self._mf6.finalize_time_step()
                yield current_time
            else:
                self._mf6.prepare_time_step(dt)
                for sol_number, max_iter in zip(sol_numbers, max_iters):
                    self._mf6.prepare_solve(sol_number)
                    for iter in range(max_iter):
                        has_converged = self._mf6.solve(sol_number)
                        if not new_step_only:
                            yield current_time
                        if has_converged:
                            if self.verbose:
                                print(
                                    f'solution {sol_number} has converged with'
                                    f' {iter} iterations'
                                )
                            break
                    self._mf6.finalize_solve(sol_number)
                self._mf6.finalize_time_step()
            current_time = self.get_current_time()
        self.finalize()

    def _get_sim_val(self, val_name):
        tag = self._mf6.get_var_address('SIMVALS', self.name, val_name.upper())
        return self._mf6.get_value_ptr(tag)

    def goto_stress_period(self, stress_period=0):
        """Progress to beginning of stress period."""
        for sim, state in self.loop:
            if state == States.timestep_start:
                model = sim.get_model()
                if model.kper == stress_period:
                    break


class MF6Docs:
    """Docstring form MF6 Fortran source."""

    def __init__(self, mf6_doc_path):
        self.mf6_doc_path = mf6_doc_path
        self._docs = {}

    def get_doc(self, name):
        """Get docs from json file."""
        if not self._docs:
            path = self.mf6_doc_path / 'mem_var_docs.json'
            with open(path, encoding='utf-8') as fobj:
                self._docs = json.load(fobj)
        return self._docs.get(name)


class Model:
    """One MF6 model."""

    _solution_value_mapping = {
        'gwf6': 'head',
        'gwt6': 'conc',
        'gwe6': 'temperature',
        'prt6': 'particles',
    }

    def __init__(self, mf6_model, state, type):
        self._model = mf6_model
        self.state = state
        self.type = type
        setattr(self, self._solution_value_mapping[type], mf6_model.X)

    def get_available_attribute_names(self):
        """Get all public attribute names of the model."""
        return [attr for attr in dir(self._model) if not attr.startswith('_')]

    def __getattr__(self, name):
        return getattr(self._model, name)


class Packages:
    """Available packages for one model."""

    def __init__(self, package_dict):
        def as_mutable_bc(self):
            """Turn package in a mutable boundary condition."""
            return create_mutable_bc(self)

        _packages = []
        for name, obj in package_dict.items():
            meta = {
                'name': name,
                'description': str(obj).splitlines()[0].strip(),
                'is_mutable': False,
                'package': obj,
            }
            if hasattr(obj, 'stress_period_data'):
                meth = MethodType(as_mutable_bc, obj)
                setattr(obj, 'as_mutable_bc', meth)
                meta['is_mutable'] = True
            if name.isidentifier():
                setattr(self, name, obj)
            _packages.append(meta)
        self._packages = pd.DataFrame(_packages).set_index('name')
        info_path = Path(__file__).parent / 'resources' / 'infos' / 'out'
        self._html_description = (info_path / 'packages.html').read_text(
            encoding='utf-8'
        )
        self._description = (info_path / 'packages.txt').read_text(
            encoding='utf-8'
        )
        self._package_dict = package_dict

    def __repr__(self):
        text = repr(self._packages[['description', 'is_mutable']])
        text += '\n\n' + self._description
        return text

    def _repr_html_(self):
        text = self._packages[['description', 'is_mutable']]._repr_html_()
        text += self._html_description
        return text

    def __getattr__(self, name):
        return getattr(self._packages, name, None)

    def get_package(self, name):
        return self._package_dict[name]


class ModelStep:
    """Object holding information about the current step."""

    def __init__(self, simulation_group, state, do_solution_loop):
        self.simulation_group = simulation_group
        self.state = state
        self.do_solution_loop = do_solution_loop

    @property
    def available_states(self):
        """Available callback states."""
        all_names = list(
            name for name in dir(States) if not name.startswith('_')
        )
        if not self.do_solution_loop:
            selection = []
            for name in all_names:
                for prefix in ['iteration_', 'stress_period_']:
                    if prefix in name:
                        break
                else:
                    selection.append(name)
        else:
            selection = all_names
        return [getattr(States, name) for name in selection]
