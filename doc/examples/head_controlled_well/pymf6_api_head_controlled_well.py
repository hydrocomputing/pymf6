from pymf6.mf6 import MF6
from pymf6.api import States
from pymf6.api import create_mutable_bc


def run_model(sim_path):
    mf6 = MF6(sim_path)
    tolerance = 0.01
    head_limit = 0.5
    lower_limit = head_limit - tolerance
    upper_limit = head_limit + tolerance
    been_below = False
    wel_coords=(0, 4, 4)
    gwf = mf6.models['gwf6']
    wel = create_mutable_bc(gwf.wel)
    for model in mf6.model_loop():
        if model.state == States.timestep_start:
            if model.kper == 2:
                pumping = model.wel.stress_period_data.values[-1][-1]
                wel_head = model.X.__getitem__(wel_coords)
                if wel_head <= lower_limit:
                    wel.q = pumping * 0.9
                    been_below = True
                elif been_below and wel_head >= upper_limit:
                    wel.q = pumping * 1.1

if __name__ == '__main__':
    run_model(r'models/pymf6')
    print('done')
