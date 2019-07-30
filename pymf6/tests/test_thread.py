#!/usr/bin/env python

"""Simple callback test in a thread
"""

from pymf6.threaded import MF6


def main():
    """
    Simple interactive test
    """
    model = MF6()
    print(f'>>> Python: Called {model.mf6.counter} times')
    print('NPER', model.mf6.get_value('NPER', 'TDIS'))
    model.next_step()
    print(f'>>> Python: Called {model.mf6.counter} time')
    input('Step 1. Press enter to continue ...')
    finished = False
    while True:
        model.next_step()
        print(f'>>> Python: Called {model.mf6.counter} times')
        print('NPER', model.mf6.get_value('NPER', 'TDIS'))
        print('Press enter to continue.')
        user_input = input('Type "end" to run to end of simulation: ')
        finished = user_input.lower().strip() == 'end'
        if finished:
            model.run_to_end()
            break


if __name__ == '__main__':
    main()
