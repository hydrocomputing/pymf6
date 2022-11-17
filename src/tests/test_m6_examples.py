

from pathlib import Path
import os
from subprocess import CalledProcessError, run
from turtle import st


MF6_EXAMPLE_PATH = os.getenv('MF6_EXAMPLE_PATH')
ERROR_FILE = 'errors.txt'
NORMAL = 'Normal termination of simulation.'


def run_model(nam_file, py_prog):
    """Run one model in a subprocess.

    Returns `True` if run was successful or `False` if not.
    """
    try:
        run(
            [
                'python',
                py_prog,
                 str(nam_file)
                 ],
            capture_output=True,
            check=True,
            )
        return True
    except CalledProcessError:
        return False


def test_run_all(
    mode='xmipy',
    example_dir=Path(MF6_EXAMPLE_PATH),
    error_file=ERROR_FILE):
    """Run all models in sub-path of `example_dir`.

    Successful model runs prints a `.`, failed one a `f`to screen.
    In addition the full paths of name files of failed runs written to
    `error_file`.
    """
    if mode == 'xmipy':
        py_prog = 'run_xmipy_model.py'
    elif mode == 'pymf6':
        py_prog = 'run_model.py'
    else:
        raise ValueError(f'mode {mode} not supported')
    with open(error_file, 'w', encoding='utf-8') as errors:
        root = example_dir.resolve()
        for root, _, files in os.walk(example_dir):
            for file_name in files:
                if file_name == 'mfsim.nam':
                    normal_termination = False
                    base = Path(root)
                    nam_file = base / 'mfsim.nam'
                    success = run_model(nam_file=nam_file, py_prog=py_prog)
                    if success:
                        stdout_file = base / 'mfsim.stdout'
                        with open(stdout_file) as stdout:
                            for line in stdout:
                                if line.strip() == NORMAL:
                                    normal_termination = True
                                    break
                    if normal_termination:
                        print('.', end='', flush=True)
                    else:
                        print('f', end='', flush=True)
                        errors.write(f'Error with: {nam_file}\n')
    print()


if __name__ == '__main__':
    test_run_all(mode='xmipy')
    test_run_all(mode='pymf6')
