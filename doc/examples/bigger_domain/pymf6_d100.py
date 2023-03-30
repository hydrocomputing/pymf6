from pymf6.mf6 import MF6

def run_model(nam_file):
    mf6 = MF6(nam_file=nam_file, dll_path=r'C:/Users/Lucia Pedrosa/mf6.4.1/bin/libmf6.dll')
    head = mf6.vars['SLN_1/X'] # solution one
    wel_index_in = 22
    wel_index_in_1 = 72
    wel_index_out = 26
    wel_index_out_1 = 76
    tolerance = 0.01
    head_limit = 0.7
    wel_in_pos = (0, 0)
    wel_in_pos_1 = (1, 0)
    wel_out_pos = (2, 0)
    wel_out_pos_1 = (3, 0)
    upper_limit = head_limit + tolerance
    lower_limit = head_limit - tolerance
    wel = mf6.vars['SYSINOUTWEL_D100/WEL_0/BOUND'] # name variable regarding well
    been_below = False
    for step in mf6.steps():
        if step < 21:
            if head[wel_index_out] <= upper_limit:
                 wel[wel_out_pos] *= 0.9
                 been_below = True
            elif been_below and head[wel_index_in] >= upper_limit:
                 wel[wel_out_pos] *= 1.1
            wel[wel_in_pos] = -wel[wel_out_pos]
            # second system of wells
            if head[wel_index_in_1] <= upper_limit:
                 wel[wel_out_pos_1] *= 0.9
                 been_below = True
            elif been_below and head[wel_index_in_1] >= upper_limit:
                 wel[wel_out_pos_1] *= 1.1
            wel[wel_in_pos_1] = -wel[wel_out_pos_1]


            # # second system
            # if lower_limit < head[wel_index_out_1] < upper_limit:
            # # if the head is between the limits then ths system circulates
            #     wel[wel_in_pos_1] = -wel[wel_out_pos_1]
            # if head[wel_index_out_1] <= lower_limit:
            # # if the head is below the limit then only injection
            #     wel[wel_out_pos_1] *= 0
            #     wel[wel_in_pos_1] *= 1.1
            # elif head[wel_index_out_1] >= upper_limit:
            # # if the head is above the limit then extraction
            #     wel[wel_out_pos_1] *= 1.1
            #     wel[wel_in_pos_1] *= 0

if __name__ == '__main__':
    run_model(r'models/pymf6/mfsim.nam')