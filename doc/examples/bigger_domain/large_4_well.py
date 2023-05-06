
from pymf6.mf6 import MF6
from pymf6.api import States

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file)
    tolerance = 0.01
    head_limit = 0.5
    lower_limit = head_limit - tolerance
    upper_limit = head_limit + tolerance
    wel_1_out_coords = (0, 20, 60)
    wel_2_out_coords = (0, 70, 60)
    wel_1_in_coords = (0, 20, 20)
    wel_2_in_coords =(0, 70, 20)
    upper_limit = 9.5
    lower_limit = 9.48
    first = True
    been_above_1 = False
    been_above_2 = False
    for sim, state in mf6.loop:
        if state == States.timestep_start:
            ml = sim.get_model()
            if ml.kper == 2:
                wells = ml.wel.stress_period_data["flux"]
                if first:
                    wel_1_out_q = wells[0]
                    wel_2_out_q = wells[1]
                    wel_1_in_q = wells[2]
                    wel_2_in_q = wells[3]
                    first = False
                wel_1_out_head = ml.X.__getitem__(wel_1_out_coords)
                wel_2_out_head = ml.X.__getitem__(wel_2_out_coords)
                wel_1_in_head = ml.X.__getitem__(wel_1_in_coords)
                wel_2_in_head = ml.X.__getitem__(wel_2_in_coords)
                wel_bc = ml.wel.stress_period_data
                if wel_1_in_head > upper_limit:
                    wells[0] = wells[0] * 0.9
                    been_above_1 = True
                elif been_above_1 and wel_1_in_head < lower_limit:
                    wells[0] = wells[0] * 1.1
                if wel_2_in_head > upper_limit:
                    wells[1] = wells[1] * 0.9
                    been_above_2
                elif been_above_2 and wel_2_in_head < lower_limit:
                    wells[1] = wells[1] * 1.1
                wells[2] = -wells[0]
                wells[3] = -wells[1]
                wel_bc["flux"] = wells

if __name__ == '__main__':
    run_model(r'models/pymf6/mfsim.nam')