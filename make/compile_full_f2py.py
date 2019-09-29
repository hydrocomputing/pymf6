"""Compile MF6 as Python extension, using `f2py`.
"""

from os import getcwd, listdir, walk
from os.path import join
from shutil import move, copy
from subprocess import call


CMD = 'f2py'
SRC = '../fsrc'


def copy_mf6_source(src, dst):
    """Copy all f90 files from the source.

    Flatten into a single dir.
    """
    valid = ['f90']
    for root, _, files in walk(src):
        for file_name in files:
            name, ext = file_name.split('.')
            if ext in valid:
                new_file_name = name + '.f90'
                copy(join(root, file_name), join(dst, new_file_name))
    return


def read_order(make_file_name, exclude=('mf6sub', 'mf6'),
               prefix='../mfsrc'):
    """Reader order of file names for compilation from Makefile.
    """
    res = []
    start = False
    exclude = ['compilerversion', 'mf6sub', 'mf6']
    with open(make_file_name) as fobj:
        for line in fobj:
            if line.startswith('OBJECTS ='):
                start = True
            if start and not line.strip():
                break
            if start and line.startswith('$(OBJDIR)'):
                name = line.split('/')[-1].split('.')[0]
                if name in exclude:
                    continue
                res.append(f'{prefix}/{name}.f90')
    return res


def compile_ext(cmd=CMD,
                make_file_name='/Users/mike/Dev/modflow6/pymake/makefile'):
    """Compile with `f2py`
    """
    n = 5
    pyf_cmd = [cmd, '--overwrite-signature',
                    '../fsrc/mf6sub.f90',
                    '../fsrc/shared_data.f90',
                    '../fsrc/access_memory.f90',
               '-m', 'mf6',
               '-h', 'mf6.pyf']
    compile_cmd = [cmd,
                   '--f90flags=-O2 -fbacktrace',
                   '-c',
                   'mf6.pyf',
                   ]
    order = read_order(make_file_name)
    compile_cmd.extend(order[:n])
    compile_cmd.append('../fsrc/compilerversion.f90')
    compile_cmd.extend(order[n:])
    compile_cmd.extend(
        [
            '../fsrc/mf6sub.f90',
            '../fsrc/shared_data.f90',
            '../fsrc/access_memory.f90',
        ]
    )

    call(pyf_cmd)
    call(compile_cmd)

    for fname in listdir(getcwd()):
        if fname.endswith('.so') or fname.endswith('.pyd'):
            move(fname, f'../pymf6/{fname}')

def main(src='/Users/mike/Dev/modflow6/src/', dst='../mfsrc'):
    """Compile"""
    copy_mf6_source(src, dst)
    compile_ext()

if __name__ == '__main__':
    main()
