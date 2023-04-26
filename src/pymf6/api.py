"""modflowapi interface
"""

from enum import Enum
import pathlib
import platform

from modflowapi import ModflowApi
from modflowapi.extensions.apisimulation import ApiSimulation
from modflowapi import Callbacks


class States(Enum):
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
        print(*cls._member_names_, sep='\n')

class Simulator:

    def __init__(self, dll, sim_path, verbose=False, _develop=False):
        """
        Generator to run a Modflow simulation using the MODFLOW-API
        with a loop

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
        self.dll = dll
        self.sim_path = sim_path
        self.verbose = verbose
        self._develop = _develop
        self._mf6 = None

    def loop(self):
        dll = self.dll
        sim_path = self.sim_path
        verbose = self.verbose
        _develop = self._develop

        ext = pathlib.Path(dll).suffix
        dll = str(dll)
        if not ext:
            if platform.system().lower() == "windows":
                dll += ".dll"
            elif platform.system().lower() == "linux":
                if not dll.startswith("./"):
                    if not dll.startswith("/"):
                        dll = "./" + dll + ".so"
                    else:
                        dll = "." + dll + ".so"
            else:
                dll += ".dylib"

        mf6 = ModflowApi(
            dll,
            working_directory=sim_path,
        )
        self._mf6 = mf6
        if verbose:
            version = mf6.get_version()
            print(f"MODFLOW-6 API Version {version}")
            print("Initializing MODFLOW-6 simulation")

        mf6.initialize()
        sim = ApiSimulation.load(mf6)

        if _develop:
            with open("var_list.txt", "w") as foo:
                for name in mf6.get_input_var_names():
                    foo.write(f"{name}\n")

        yield sim, States.initialize

        has_converged = False
        current_time = mf6.get_current_time()
        end_time = mf6.get_end_time()
        kperold = [0 for _ in range(sim.subcomponent_count)]

        while current_time < end_time:
            dt = mf6.get_time_step()
            mf6.prepare_time_step(dt)

            if verbose:
                print(
                    f"Solving: Stress Period {sim.kper + 1}; "
                    f"Timestep {sim.kstp + 1}"
                )

            for sol_id, slnobj in sorted(sim.solutions.items()):
                models = {}
                maxiter = slnobj.mxiter
                solution = {sol_id: slnobj}
                for model in sim.models:
                    if sol_id == model.solution_id:
                        models[model.name.lower()] = model

                sim_grp = ApiSimulation(
                    mf6, models, solution, sim._exchanges, sim.tdis, sim.ats
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

            mf6.finalize_time_step()
            current_time = mf6.get_current_time()

            if not has_converged:
                print(f"Simulation group: {sim_grp} DID NOT CONVERGE")

            if sim_grp.nstp == sim_grp.kstp + 1:
                yield sim_grp, States.stress_period_end

        try:
            yield sim, States.finalize
            mf6.finalize()
        except Exception:
            raise RuntimeError("MF6 simulation failed, check listing file")

        print("NORMAL TERMINATION OF SIMULATION")