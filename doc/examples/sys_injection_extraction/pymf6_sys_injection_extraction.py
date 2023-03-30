from pymf6.mf6 import MF6

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file, dll_path = r"C:/Users/Lucia Pedrosa/mf6.4.1/bin/libmf6.dll")
    head = mf6.vars['SLN_1/X'] # solution one
    wel_index_in = 11
    wel_index_out = 88
    obs = 55
    tolerance = 0.01
    head_limit = 0.7
    wel_in_pos = (0, 0)
    wel_out_pos = (1, 0)
    upper_limit = head_limit + tolerance
    lower_limit = head_limit - tolerance
    wel = mf6.vars['SYSINOUTWEL/WEL_0/BOUND'] # name variable regarding well
    been_below = False
    for step in mf6.steps():
        if step < 21:
            if head[wel_index_out] <= upper_limit:
                 wel[wel_out_pos] *= 0.9
                 been_below = True
            elif been_below and head[wel_index_out] >= upper_limit:
                 wel[wel_out_pos] *= 1.1
            wel[wel_in_pos] = -wel[wel_out_pos]


if __name__ == '__main__':
    run_model(r'models/mf6/mfsim.nam')