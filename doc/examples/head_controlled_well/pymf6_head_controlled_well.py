from pymf6.mf6 import MF6

def run_model(sim_path):
    mf6 = MF6(sim_path)
    head = mf6.vars['SLN_1/X']
    wel_index = 44
    tolerance = 0.01
    head_limit = 0.5
    upper_limit = head_limit + tolerance
    lower_limit = head_limit - tolerance
    wel = mf6.vars['HEADCONWELL/WEL_0/BOUND']
    been_below = False
    for step in mf6.steps:
        if step < 21:
            if head[wel_index] <= lower_limit:
                wel[:] = wel[:] * 0.9
                been_below = True
            elif been_below and head[wel_index] >= upper_limit:
                wel[:] = wel[:] * 1.1


if __name__ == '__main__':
    run_model('models/pymf6')
    print('done')
