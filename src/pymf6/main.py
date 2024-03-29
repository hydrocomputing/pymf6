"""Main"""


import sys

from .mf6 import MF6
from .tools.info import show_info


def run_model(nam_file):
    """Run one model without modifications."""
    text = f'running {nam_file}'
    line = '=' * len(text)
    print(line)
    print(text)
    print(line)
    try:
        mf6 = MF6(nam_file=nam_file)
        for _ in mf6.steps():
            pass
        print(f'GOOD {nam_file}')
    except Exception as err:
        print(f'BAD {nam_file}')
        raise err
    print(line)
    print(line)


def main():
    """Main program of pymf6"""
    args = sys.argv
    if len(args) == 2:
        run_model(args[1])
    else:
        show_info()


if __name__ == '__main__':
    main()
