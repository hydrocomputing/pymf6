"""
Wrapper around XmiWrapper.
"""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError
from xmipy.utils import cd

from . datastructures import Simulation
from .tools.info import get_info, info, read_ini


class MF6:
    """
    Wrapper around XmiWrapper.
    """
    # pylint: disable=too-many-instance-attributes

    # Only one instance can be initialized but not finalized.
    # Store the active instance here to improve interactive
    # experience in Notebooks.
    old_mf6 = None

    def __init__(self, nam_file=None, sim_file='mfsim.nam', dll_path=None):

        def init_mf6():
            # Finalize if initialized instance exists.
            # This is helpful for interactive work in Notebooks.
            # Use class `MF6` nit `self.__class__` to prevent child class
            # from initializing an instance at the same time an instance of
            # the parent class is still initialized.
            if MF6.old_mf6:
                MF6.old_mf6.finalize()
            self._mf6 = XmiWrapper(str(self.dll_path))
            MF6.old_mf6 = self._mf6
        self._infos = get_info()
        self.ini_path, self.ini_data = read_ini()
        if dll_path is None:
            if self.ini_data is None:
                raise ValueError(
                    'No DLL path and no ini file found.\n'
                    'Please provide the DLL path as argument or '
                    'create an ini file with the path to MODFLOW 6 DLL.'
                    )
            self.dll_path = Path(self.ini_data['paths']['dll_path'])
        else:
            self.dll_path = Path(dll_path)
        if nam_file:
            self.nam_file = Path(nam_file).resolve()
            self.model_path = self.nam_file.parent
            self.sim_file = self.model_path / sim_file
            with cd(self.model_path):
                init_mf6()
                self._mf6.initialize(str(self.nam_file))
                self.__class__.is_initialized = True
                self.simulation = Simulation(self._mf6, self.sim_file)
                self.vars = self._get_vars()
        else:
            init_mf6()

    def _repr_html_(self):
        """
        Make a nice HTML table
        :param obj: Python object
        :return: HTML string
        """
        html_text = '<h3>MF6</h3>'
        html_text += '<h4>pymf6 configuration data</h4>'
        html_text += '<table><tbody>'
        for name, value in self._infos.items():
            if not name.startswith('_'):
                html_text += f'<tr><td>{name}:</td>'
                html_text += f'<td>{value}</td></tr>'
        html_text += '</tbody></table>'
        return html_text

    @property
    def info(self):
        """Information about versions and paths."""
        info(self._infos)

    def finalize(self):
        """Finalize the model run."""
        self._mf6.finalize()

    def do_time_step(self):
        """Do one time step."""
        self._mf6.do_time_step()

    def get_current_time(self):
        return self._mf6.get_current_time()

    def get_end_time(self):
        return self._mf6.get_end_time()

    def update(self):
        return self._mf6.update()


    @property
    def version(self):
        return self._mf6.get_version()

    def _get_vars(self):
        """Get all variables in dictionary.

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


    def steps(self):
        """Generator for iterating over all time steps.
        It allows to modify MODFLOW variables for each time
        step.

        Example:

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
        while current_time < end_time:
            dt = self._mf6.get_time_step()
            self._mf6.prepare_time_step(dt)
            yield current_time
            self._mf6.do_time_step()
            self._mf6.finalize_time_step()
            current_time = self.get_current_time()
        self.finalize()

