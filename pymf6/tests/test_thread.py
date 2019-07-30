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
        print('Type "end" to run to end of simulation.')
        print('Type "all" to show all names.')
        print('Enter <name>, <group> separated by comma to show value.')
        user_input = input('Your input: ').lower().strip()
        if user_input == 'end':
            model.run_to_end()
            break
        elif user_input == 'all':
            for counter, (name, group) in enumerate(model.names, 1):
                print(counter, name, group, sep=', ')
        elif ',' in user_input:
            name, group = [x.strip().upper() for x in user_input.split(',')]
            value = model.get_value(name, group)
            print(name, group, value.dtype, value.shape, value)


if __name__ == '__main__':
    main()
