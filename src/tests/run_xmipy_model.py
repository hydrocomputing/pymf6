
from pathlib import Path
import os
import sys

from xmipy import XmiWrapper
from xmipy.utils import cd

DLL_PATH = os.getenv('DLL_PATH')

def run_model(dll_path=DLL_PATH):
    nam_file = sys.argv[1]
    model_path = str(Path(nam_file).parent)
    with cd(model_path):
        try:
            print('#' * 80)
            print(f'    START {nam_file}')
            mf6 = XmiWrapper(dll_path)
            print(f'    INSTANCE')
            mf6.initialize(nam_file)
            print(f'    INITIALIZED')
            current_time = mf6.get_current_time()
            end_time = mf6.get_end_time()
            print(f'    LOOP START')
            while current_time < end_time:
                mf6.update()
                current_time = mf6.get_current_time()
            mf6.finalize()
            print(f'    FINALIZED')
            print(f'    GOOD {nam_file}')
        except:
            print(f'     BAD {nam_file}')
            raise
    print(f'    END')



if __name__ == '__main__':
    run_model()
