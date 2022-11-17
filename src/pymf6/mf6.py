"""
Wrapper around XmiWrapper.
"""

from configparser import ConfigParser
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError
from xmipy.utils import cd

from . datastructures import Simulation


class MF6:
    """
    Wrapper around XmiWrapper.
    """
    # pylint: disable=too-many-instance-attributes

    # Only one instance can be intitialzed but not finalized.
    # Store the active instance here to improve interactive
    # experience in Notebooks.
    old_mf6 = None

    def __init__(self, nam_file, sim_file='mfsim.nam', dll_path=None):

        self.nam_file = Path(nam_file).resolve()
        self.model_path = self.nam_file.parent
        self.sim_file = self.model_path / sim_file
        self.ini_path, self.ini_data = self._read_ini()
        if dll_path is None:
            self.dll_path = Path(self.ini_data['paths']['dll_path'])
        else:
            self.dll_path = Path(dll_path)
        with cd(self.model_path):
            # Finalze if intialized instance exists.
            # This is helpful for interactive work in Notebooks.
            # Use class `MF6` nit `self.__class__` to prevent child class
            # from intializing an instance at the same time an instance of
            # the parent class is still intialzed.
            if MF6.old_mf6:
                MF6.old_mf6.finalize()
            self._mf6 = XmiWrapper(str(self.dll_path))
            MF6.old_mf6 = self._mf6
            self._mf6.initialize(str(self.nam_file))
            self.__class__.is_initialized = True
            self.simulation = Simulation(self._mf6, self.sim_file)
            self.vars = self._get_vars()

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

    def _read_ini(self):
        """Read ini file.

        This looks for `pymf6.ini` in the current working directory
        first. If not found there, it looks in the user's home directory.
        If no file is found `ini_data` will be `None`.
        """
        ini_path = Path('pymf6.ini')
        if not ini_path.exists():
            ini_path = ini_path.home() / ini_path
        if not ini_path.exists():
            ini_path = None
        if ini_path:
            ini_path = ini_path.resolve()
            parser = ConfigParser()
            parser.read(ini_path)
            ini_data = parser
        else:
            ini_data = None
        return ini_path, ini_data

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