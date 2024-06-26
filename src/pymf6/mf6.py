"""Wrapper around XmiWrapper."""

from contextlib import redirect_stdout
import json
from io import StringIO
from pathlib import Path

from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError
from xmipy.utils import cd

from . api import Simulator, States
from . datastructures import Simulation
from .tools.info import (
    get_info_data,
    show_info,
    make_info_texts,
    make_info_html,
    read_ini)


class MF6:
    """Wrapper around XmiWrapper."""

    # pylint: disable=too-many-instance-attributes

    # Only one instance can be initialized but not finalized.
    # Store the active instance here to improve interactive
    # experience in Notebooks.
    old_mf6 = None
    _demo = False

    def __init__(
            self,
            nam_file=None,
            sim_file='mfsim.nam',
            dll_path=None,
            use_modflow_api=True,
            verbose=False,
            _develop=False
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
                    _develop=_develop)
                # pylint: disable=protected-access
                self._mf6 = self._simulator._mf6
                self.api = self._simulator.api
                models = {}
                self._reverse_names = {}
                for index, name in enumerate(self.api.model_names, start=1):
                    name = name.lower()
                    prefix_parts = name.split('_', 1)
                    if len(prefix_parts) == 1:
                        prefix = 'gwf'
                    else:
                        prefix = prefix_parts[0]
                    if prefix in models:
                        msg = 'Multiple models in one solution no supported yet.'
                        raise NotImplementedError(msg)
                    model = self.api.get_model(index)
                    models[prefix] = model
                    self._reverse_names[name] = prefix
                self.models = models


            else:
                self._mf6 = XmiWrapper(str(self.dll_path))
                self._mf6.initialize(str(self.nam_file))
            MF6.old_mf6 = self._mf6

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

        if dll_path is None:
            self.dll_path = ini_data['dll_path']
        else:
            self.dll_path = Path(dll_path)
        if nam_file:
            self.nam_file = Path(nam_file).resolve()
            if not self.nam_file.exists():
                raise FileNotFoundError(self.nam_file)
            self.model_path = self.nam_file.parent
            self.sim_file = self.model_path / sim_file
            with cd(self.model_path):
                init_mf6(str(self.nam_file.parent))
                self.__class__.is_initialized = True
                self.simulation = Simulation(
                    self._mf6,
                    self.sim_file,
                    self.mf6_docs)
                self.vars = self._get_vars()
        else:
            init_mf6(str(self.nam_file.parent))
        if use_modflow_api:
            self.sol_loop = self._simulator.loop()
        else:
            self.sol_loop = None

    def model_loop(self):
        """Timestep loop over all models."""
        for sol_group, state in self.sol_loop:
            mf6_model = sol_group.get_model()
            model_type = self._reverse_names[mf6_model.name.lower()]
            yield Model(mf6_model=mf6_model, state=state, type=model_type)

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

    def steps(self, new_step_only=False):
        """
        Provide a generator for iterating over all time steps.

        It allows to modify MODFLOW variables for each time step.
        new_step_only -yield only at new time step

        If `new_step_only` is set to `True` each step has new value.
        Otherwise the control is gain for each outer iteration,
        resulting in getting the same time step multiple times (<= `MXITER`).
        Do **NOT** set  `new_step_only` to `True` if modifying time
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
            self._mf6.prepare_time_step(dt)
            for sol_number, max_iter in zip(sol_numbers, max_iters):
                self._mf6.prepare_solve(sol_number)
                for iter in range(max_iter):
                    has_converged = self._mf6.solve(sol_number)
                    if not new_step_only:
                        yield current_time
                    if has_converged:
                        if self.verbose:
                            print(f'solution {sol_number} has converged with'
                                  f' {iter} iterations')
                        break
                self._mf6.finalize_solve(sol_number)
            self._mf6.finalize_time_step()
            if new_step_only:
                yield current_time
            current_time = self.get_current_time()
        self.finalize()

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
        'gwf': 'head',
        'gwt': 'conc',
        'gwe': 'temperature',
    }

    def __init__(self, mf6_model, state, type):
        self._model = mf6_model
        self.state = state
        self.type = type
        setattr(self, self._solution_value_mapping[type], mf6_model.X)

    def __getattr__(self, name):
        return getattr(self._model, name)
