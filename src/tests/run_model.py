

import sys

from pymf6.mf6 import MF6


def run_model():
    nam_file=sys.argv[1]
    try:
        print('#' * 80)
        mf6 = MF6(nam_file=nam_file)
        print(f'    START {nam_file}')
        mf6 = XmiWrapper(dll_path)
        print(f'    INSTANCE')
        mf6.initialize(nam_file)
        print(f'    INITIALIZED')
        current_time = mf6.get_current_time()
        end_time = mf6.get_end_time()

        while current_time < end_time:
            mf6.update()
            current_time = mf6.get_current_time()
        mf6.finalize()
        print(f'    GOOD {nam_file}')
    except:
        print(f'    BAD {nam_file}')
        raise



if __name__ == '__main__':
    run_model()

