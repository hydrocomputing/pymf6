
import os
from pathlib import Path
import sys

from pymf6.mf6 import MF6

DLL_PATH = os.getenv('DLL_PATH')

def run_model():
    nam_file=sys.argv[1]
    model_dir = Path(nam_file).parent
    try:
        print('#' * 80)
        mf6 = MF6(
            nam_file=nam_file,
            sim_file=model_dir / 'mfsim.nam',
            dll_path=DLL_PATH)
        print(f'    START {nam_file}')
        print(f'    INSTANCE')
        current_time = mf6.get_current_time()
        end_time = mf6.get_end_time()
        print(f'    LOOP START')
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
