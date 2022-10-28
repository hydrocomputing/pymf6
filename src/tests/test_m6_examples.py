

from pathlib import Path
import os
from subprocess import run


MF6_EXAMPLE_PATH = os.getenv('MF6_EXAMPLE_PATH')


def run_model(nam_file):
    run(['python', 'run_xmipy_model.py', str(nam_file)])


def test_run_all(example_dir=Path(MF6_EXAMPLE_PATH)):
    root = example_dir.resolve()
    for model_path in root.iterdir():
        nam_file = model_path / 'mfsim.nam'
        print(f'RUNNING {nam_file}')
        run_model(nam_file=nam_file)
        print(f'DONE {nam_file}')
        print()


if __name__ == '__main__':
    test_run_all()
