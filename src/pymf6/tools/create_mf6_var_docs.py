"""Create documentation information for MF6 variable names.

MODFLOW provides meta infomation of input variables in a structured format.
The directory `modflow6/doc/mf6io/mf6ivar/dfn` contains multiple files with
these entries. See `modflow6/doc/mf6io/mf6ivar/readme.md` for details.

The files are read, converted to dictionaries  and dumped as JSON.
The files have the form `gwf-evt.dfn` and `gwf-buy.dfn`.
Here we use the terminology category and package for the name parts.

The output lands in `resources/mf6_var_names` and has the form
`<tag>/<category>/<package>.json`
"""

import json
import os
from pathlib import Path
from subprocess import run
import sys

import pymf6

MF6_VAR_DIR = (Path().home() / 'Dev/modflow6/doc/mf6io/mf6ivar').absolute()
OUT_DIR = (Path(pymf6.__file__).parent / 'resources/mf6_var_names').absolute()


class VersionTag:
    """Context manager for a version tag.

    This switches to the tag position with `git switch --detach <tag>`
    in `__enter__`and back to `develop in `__exit__`
    """

    def __init__(self, tag, mf6_var_dir=MF6_VAR_DIR, out_dir=OUT_DIR):
        assert len(int(entry) for entry in tag.split('.')) == 3
        self.tag = tag
        self.mf6_var_dir = mf6_var_dir
        self.dfn_dir = self.mf6_var_dir / 'dfn'
        self.out_dir_tag = out_dir / tag
        self.out_dir_tag.mkdir(exist_ok=True)
        self.git = sys.prefix + '/bin/git'
        self.old_dir = None
        self.mf6ivar = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.mf6_var_dir)
        sys.path.append(str(self.mf6_var_dir))
        import mf6ivar  # pylint: disable=import-outside-toplevel, import-error
        self.mf6ivar = mf6ivar
        del sys.path[-1]
        run([self.git, 'switch', '--detach', self.tag], check=True)
        return self

    def __exit__(self, *args):
        run([self.git, 'switch', 'develop'], check=True)
        os.chdir(self.old_dir)


def _make_description(
    entries,
    mf6ivar,
    token='description',
    replace_text=(
        ('\\_', '_'),
        ('``', '""'),
        ("''", '""'))):
    """Create the description.

    This replaces all "REPLACE" entries and removes LaTeX formatting.
    See `modflow6/doc/mf6io/mf6ivar/readme.md` for details of the
    replacement.
    """
    for entry in entries.values():
        if token in entry:
            text = mf6ivar.get_description(entry[token])
            for to_replace in replace_text:
                text = text.replace(*to_replace)
            entry[token] = text
    return entries


def _write_docs(file_name, var_docs, out_dir):
    """Write JSON to files.

    Creates the file with the pattern `<tag>/<category>/<package>.json`.
    """
    try:
        category, package = file_name.split('.')[0].split('-')
    except ValueError:
        print(f'skipping {file_name}')
        return
    out_sub_dir = out_dir / category
    out_sub_dir.mkdir(exist_ok=True)
    out_name = out_sub_dir / f'{package}.json'
    with open(out_name, encoding='utf-8', mode='w') as fobj:
        json.dump(var_docs, fobj)


def save_var_docs(tag):
    """Save MF6 variable documentation to JSON files."""
    with VersionTag(tag) as version_tag:
        for file_name in os.listdir(version_tag.dfn_dir):
            file_path = version_tag.dfn_dir / file_name
            mf6_vars = version_tag.mf6ivar.parse_mf6var_file(file_path)
            var_docs = {key[0]: value for key, value in mf6_vars.items()}
            var_docs = _make_description(var_docs, mf6ivar=version_tag.mf6ivar)
            _write_docs(
                file_name=file_name,
                var_docs=var_docs,
                out_dir=version_tag.out_dir_tag)


if __name__ == '__main__':
    save_var_docs('6.4.1')
