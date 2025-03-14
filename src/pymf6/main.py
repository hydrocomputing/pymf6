"""Main"""


import sys

from .mf6 import MF6
from .tools.info import show_info


def run_model(sim_path):
    """Run one model without modifications."""
    text = f'running {sim_path}'
    line = '=' * len(text)
    print(line)
    print(text)
    print(line)
    try:
        mf6 = MF6(sim_path=sim_path)
        for _ in mf6.model_loop():
            pass
        print(f'GOOD {sim_path}')
    except Exception as err:
        print(f'BAD {sim_path}')
        raise err
    print(line)


def main():
    """Run main program of pymf6."""
    args = sys.argv
    if len(args) == 2:
        run_model(args[1])
    else:
        show_info()


if __name__ == '__main__':
    main()
