from pymf6.mf6 import MF6

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file)
    head = mf6.vars['SLN_1/X']
    wel_index_in = 22
    wel_index_out = 66
    tolerance = 0.01
    head_limit_out = 0.5
    head_limit_in = 0.95
    upper_limit_in = head_limit_in + tolerance
    upper_limit_out = head_limit_out + tolerance
    lower_limit_out = head_limit_out - tolerance
    wel_out, wel_in = mf6.vars['SYSINOUTWEL/WEL_0/BOUND']
    pumping_reduced = False
    init_reduce = True
    init_reduce_amount = 1
    for step in mf6.steps():
        if step >= 11 and step < 21:
            if init_reduce and  step < 11.1:
                wel_out[0] = wel_out[0] * 0.9
                init_reduce_amount *= 0.9
                if init_reduce_amount < 0.5:
                    init_reduce = False
            if ((head[wel_index_in] > upper_limit_in) or
                (head[wel_index_out] < lower_limit_out)):
                wel_out[0] = wel_out[0] * 0.99
                pumping_reduced = True
            elif pumping_reduced and head[wel_index_out] > upper_limit_out:
                wel_out[0] = wel_out[0] * 1.01
            wel_in[0] = -wel_out[0]


if __name__ == '__main__':
    run_model(r'models/pymf6/mfsim.nam')
