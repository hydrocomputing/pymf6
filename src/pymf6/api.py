"""modflowapi interface."""

from enum import Enum

from modflowapi import ModflowApi
from modflowapi.extensions.apisimulation import ApiSimulation


class States(Enum):
    """States of MODFLOW API."""

    #  pylint: disable=invalid-name
    initialize = 0
    stress_period_start = 1
    stress_period_end = 2
    timestep_start = 3
    timestep_end = 4
    iteration_start = 5
    iteration_end = 6
    finalize = 7

    @classmethod
    def show_states(cls):
        """Show available states."""
        # pylint: disable=no-member
        print(*cls._member_names_, sep='\n')

    def __eq__(self, other):
        return self.value == other.value


class Simulator:
    """
    Generator to run a Modflow simulation using the MODFLOW-API.

    with a loop
    """

    def __init__(self, dll, sim_path, verbose=False, _develop=False):
        """
        Set initial values.

        Parameters
        ----------
        dll : str
            path to the Modflow6 shared object
        sim_path : str
            path to the Modflow6 simulation
        verbose : bool
            flag for verbose output from the simulation runner
        _develop : bool
            flag that dumps a list of all mf6 api variable addresses to text
            file named "var_list.txt". This is primarily used for extensions
            development purposes and bug fixes within the modflowapi python
            package.

        """
        self.verbose = verbose
        self._develop = _develop
        self._mf6 = ModflowApi(
            dll,
            working_directory=sim_path,
        )
        self._mf6.initialize()
        self.api = ApiSimulation.load(self._mf6)
        self._sim_grp = None

    def loop(self):
        """
        Loop over all time steps.

        Provides simulation group and state for each times step.
        """
        mf6 = self._mf6
        verbose = self.verbose
        sim = self.api

        current_time = mf6.get_current_time()
        end_time = mf6.get_end_time()
        kperold = [0 for _ in range(sim.subcomponent_count)]

        while current_time < end_time:
            dt = mf6.get_time_step()  # pylint: disable=invalid-name
            mf6.prepare_time_step(dt)

            if verbose:
                print(
                    f'Solving: Stress Period {sim.kper + 1}; '
                    f'Timestep {sim.kstp + 1}'
                )
            yield from self._solutions_loop(
                sim=sim, mf6=mf6, current_time=current_time, kperold=kperold
            )
            mf6.finalize_time_step()
            current_time = mf6.get_current_time()
        try:
            mf6.finalize()
        except Exception as err:
            msg = 'MF6 simulation failed, check listing file'
            raise RuntimeError(msg) from err

        print('NORMAL TERMINATION OF SIMULATION')

    def _solutions_loop(self, sim, mf6, current_time, kperold):
        """Sub loop over solutions."""
        has_converged = False
        for sol_id, slnobj in sorted(sim.solutions.items()):
            models = {}
            maxiter = slnobj.mxiter
            solution = {sol_id: slnobj}
            for model in sim.models:
                if sol_id == model.solution_id:
                    models[model.name.lower()] = model

            sim_grp = ApiSimulation(
                # pylint: disable=protected-access
                mf6,
                models,
                solution,
                sim._exchanges,
                sim.tdis,
                sim.ats,
            )
            mf6.prepare_solve(sol_id)
            if sim.kper != kperold[sol_id - 1]:
                yield sim_grp, States.stress_period_start
                kperold[sol_id - 1] += 1
            elif current_time == 0:
                yield sim_grp, States.stress_period_start

            kiter = 0
            yield sim_grp, States.timestep_start

            if sim_grp.ats_period[0]:
                mindt = sim_grp.ats_period[-1]
                while sim_grp.delt > mindt:
                    sim_grp.iteration = kiter
                    yield sim_grp, States.iteration_start
                    has_converged = mf6.solve(sol_id)
                    yield sim_grp, States.iteration_end
                    kiter += 1
                    if has_converged and sim_grp.allow_convergence:
                        break
            else:
                while kiter < maxiter:
                    sim_grp.iteration = kiter
                    yield sim_grp, States.iteration_start
                    has_converged = mf6.solve(sol_id)
                    yield sim_grp, States.iteration_end
                    kiter += 1
                    if has_converged and sim_grp.allow_convergence:
                        break
            yield sim_grp, States.timestep_end
            mf6.finalize_solve(sol_id)
            if sim_grp.nstp == sim_grp.kstp + 1:
                yield sim_grp, States.stress_period_end
        if not has_converged:
            print(f'Simulation group: {sim_grp} DID NOT CONVERGE')
        self._sim_grp = sim_grp


def create_mutable_bc(package):
    """
    Create a mutable boundary condition.

    Create mutable object for boundary condition with stress period data.
    Assigned values will be written back to a running model.

    `package` is a MODFLOW 6 package object such as WEL or CHD.

    Usage example:

    Assess a flow model:
    >>> from pymf6.mf6 import MF6
    >>> mf6 = MF6('path/to/mfsim.nam', use_modflow_api=True)
    >>> gwf = mf6.models['gwf6']

    Create a mutable bc:
    >>> wel = create_mutable_bc(gwf.wel)

    Show current values:
    >>> wel.q

    Set new values:
    >>> wel.q = -0.2
    """
    try:
        package.stress_period_data
    except AttributeError:
        raise AttributeError(
            f'Package {package.pkg_name} does NOT have stress period data'
        )

    class MutableStressPeriodData:
        def __init__(self, package):
            col_names = package.stress_period_data.dataframe.columns
            attrs = '\n'.join(f'* {name}' for name in col_names)
            class_docstring = f"""
            Boundary condition with mutable stress period data for {package}.

            This object allows to assign new values to these attributes:

            {attrs}
            """
            setattr(self.__class__, '__doc__', class_docstring)
            self.package = package
            for col_name in col_names:
                # need name binding in function definition
                # otherwise only the last name in the loop will be stored in
                # the closure and use for all values
                def fget(self, col_name=col_name):
                    return self.package.stress_period_data.dataframe[col_name]

                def fset(self, new_values, col_name=col_name):
                    values = self.package.stress_period_data.values
                    if values is None:
                        return
                    values[col_name] = new_values
                    self.package.stress_period_data.values = values

                setattr(
                    self.__class__,
                    col_name,
                    property(
                        fget=fget,
                        fset=fset,
                        doc=f'stress period data for {col_name}',
                    ),
                )

        def __repr__(self):
            return repr(self.package.stress_period_data.dataframe)

        def _repr_html_(self):
            return self.package.stress_period_data.dataframe._repr_html_()

    return MutableStressPeriodData(package)


def find_packages_with_stress_period_data(model):
    """Find all packages of a model that have stress period data."""
    return [
        package_name for package_name in model.package_dict
        if getattr(getattr(model, package_name), 'stress_period_data', None)]
