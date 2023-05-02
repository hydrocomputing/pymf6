from pymf6.mf6 import MF6
from pymf6.api import States

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file)
    tolerance = 0.01
    head_limit = 0.5
    lower_limit = head_limit - tolerance
    upper_limit = head_limit + tolerance
    head = None
    been_below = False

    head = mf6.vars['SLN_1/X']
    wel = mf6.vars['HEADCONWELL/WEL_0/BOUND']
    wel_index = 44

    for sim, state in mf6.loop:
        if state == States.timestep_start:
            ml = sim.get_model()
            if ml.kper == 2:
                if head[wel_index] <= lower_limit:
                    wel[:] = wel[:] * 0.9
                    been_below = True
                elif been_below and head[wel_index] >= upper_limit:
                    wel[:] = wel[:] * 1.1

if __name__ == '__main__':
    run_model(r'models/pymf6/mfsim.nam')
