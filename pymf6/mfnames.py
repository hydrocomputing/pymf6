"""
Read name and origin from MODFLOW 6 *list file
"""

import pickle
import os
import subprocess


NOT_YET_SUPPORTED = set(['TIMESERIES'])


def read_lst(fname='mfsim.lst'):
    """
    Read origin and name from `mfsim.lst`file
    :param fname: simulation list name, typically `mfsim.lst`
    :return: dict with this structure:
             {
                 (name, origin): {'data_type': 'int_scalar'},
                 (name, origin): {'data_type': 'float_scalar'},
                 (name, origin): {'data_type': 'int_1d'},
                 ....
             }
    """
    mapping = {'INTEGER': 'int',
               'DOUBLE': 'float',
               'LOGICAL': 'bool'}
    data = {}
    with open(fname) as fobj:
        for line in fobj:
            if line.strip().startswith('ORIGIN'):
                break
        next(fobj)
        for line in fobj:
            if not line.strip():
                break
            origin = line[:45].strip()
            name = line[45:61].strip()
            datatype_entry = line[61:90].strip()
            raw_datatype, *raw_dim = datatype_entry.split()
            #  TODO: Support these data types too
            if raw_datatype in NOT_YET_SUPPORTED:
                continue
            data_type = mapping[raw_datatype]
            if not raw_dim:
                dim = 'scalar'
            else:
                dim = f'{len(raw_dim[0].split(","))}d'
            data[(name, origin)] = {'data_type': f'{data_type}_{dim}'}
    return data


def get_names(force_generate=False,
              pickle_fname='data_mapping.pkl',
              verbose=False,
              show_mf6_output=False):
    """
    Run MODFLOW til end with option:

        BEGIN OPTIONS
          MEMORY_PRINT_OPTION ALL
        END OPTIONS

    Read all `name`-`origin` values from `mfsim.lst` and
    write resultiong dictionary into a pickle file.
    :param force_generate: run MODFLOW 6 no matter if there is a
                           pickle with names already
    :param pickle_fname: name of pickle file for storage of names and origins
    :param verbose: show information what happens
    :return: None
    """
    capture_output = not show_mf6_output
    if not force_generate:
        try:
            with open(pickle_fname, 'rb') as fobj:
                if verbose:
                    print('Read names and origins from pickle file.')
                return pickle.load(fobj)
        except FileNotFoundError:
            pass
    cmd_file = os.path.join(os.path.split(__file__)[0], 'mf6_init_run.py')
    if verbose:
        print('Run MODFLOW calculation to generate names and origins.')
    subprocess.run(['python', cmd_file],
                   capture_output=capture_output)
    data = read_lst()
    with open(pickle_fname, 'wb') as fobj:
        pickle.dump(data, fobj)
    if verbose:
        print('Dumped names and origins into pickle file.')
    return data
