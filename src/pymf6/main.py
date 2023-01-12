"""Main"""

from os import sep
from pathlib import Path
import sys

from .mf6 import MF6
from .tools.info import info


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
        print(f'GOOD {nam_file}')
    except:
        print(f'BAD {nam_file}')
        raise
    print(line)
    print(line)


def main():
    """Main program of pymf6"""
    args = sys.argv
    if len(args) == 2:
        run_model(args[1])
    else:
        info()


if __name__ == '__main__':
    main()

