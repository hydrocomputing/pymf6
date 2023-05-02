from pymf6.mf6 import MF6
from pymf6.api import States

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file)
    tolerance = 0.01
    head_limit = 0.5
    lower_limit = head_limit - tolerance
    upper_limit = head_limit + tolerance
    been_below = False
    wel_coords=(0, 4, 4)
    for sim, state in mf6.loop:
        if state == States.timestep_start:
            ml = sim.get_model()
            if ml.kper == 2:
                pumping = ml.wel.stress_period_data["flux"]
                wel_head = ml.X.__getitem__(wel_coords)
                wel_bc = ml.wel.stress_period_data
                if wel_head <= lower_limit:
                    wel_bc["flux"] = pumping * 0.9
                    been_below = True
                elif been_below and wel_head >= upper_limit:
                    wel_bc["flux"] = pumping * 1.1

if __name__ == '__main__':
    run_model(r'models/pymf6/mfsim.nam')
