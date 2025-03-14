"""Create HTML and text docstrings from markdown."""

from pathlib import Path
from subprocess import run

import pymf6


PATH = Path(pymf6.__file__).parent / 'resources' / 'infos'


def make_dosctrings(path=PATH, out_formats=('html', 'txt')):
    """Create dostring texts from markdown."""
    in_path = path / 'in'
    for file in in_path.glob('*.md'):
        print(file)
        for ext in out_formats:
            out_file = file.parent.parent / 'out' / f'{file.stem}.{ext}'
            print(out_file)
            run(['pandoc', '-o', out_file, file], cwd=path)


if __name__ == '__main__':
    make_dosctrings()
