
import os
from pathlib import Path
import sys

from pymf6.mf6 import MF6


def run_model(nam_file):
    """Run one model without modifications."""
    text = f'running {nam_file}'
    line = '=' * len(text)
    print(line)
    print(text)
    print(line)
    try:
        mf6 = MF6(nam_file=nam_file)
        for step in mf6.steps():
            pass
        print(f'    GOOD {nam_file}')
    except:
        print(f'    BAD {nam_file}')
        raise
    print(line)
    print(line)


if __name__ == '__main__':
    run_model(nam_file=sys.argv[1])
