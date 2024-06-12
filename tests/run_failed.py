"""Run failed tests."""

import os
from pprint import pprint
from pathlib import Path
from subprocess import run



MF6_EXAMPLE_PATH = os.getenv('MF6_EXAMPLE_PATH')
ERROR_FILE = 'errors.txt'


def run_model(nam_file, py_prog):
    """Run one model in a subprocess."""
    proc = run(
            [
                'python',
                py_prog,
                 str(nam_file)
                 ],
            capture_output=True,
            encoding='utf-8',
            )
    return proc.stderr


def test_run_all_failed(
    mode='xmipy',
    error_file=ERROR_FILE):
    """Run all failed models in sub-path of `example_dir`."""
    if mode == 'xmipy':
        py_prog = 'run_xmipy_model.py'
    elif mode == 'pymf6':
        py_prog = 'run_model.py'
    else:
        raise ValueError(f'mode {mode} not supported')
    errors = {}
    with open(error_file) as fobj:
        for line in fobj:
            nam_file = line.split()[-1]
            err = run_model(nam_file=nam_file, py_prog=py_prog)
            msg = err.splitlines()[-1]
            model_name = Path(nam_file).parts[-2]
            if model_name == 'prt':
                model_name = '/'.join(Path(nam_file).parts[-3:-1])
            errors.setdefault(msg, []).append(model_name)
    pprint(errors)
    pprint({msg: len(files) for msg, files in errors.items()})


if __name__ == '__main__':
    from timeit import default_timer
    start = default_timer()
    test_run_all_failed(mode='pymf6', error_file='pymf6_error.txt')
    print(f'run time: {default_timer() - start:.2f}')
