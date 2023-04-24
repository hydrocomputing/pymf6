"""Create documentation information for MF6 variable names.

# Input Variables

MODFLOW provides meta infomation of input variables in a structured format.
The directory `modflow6/doc/mf6io/mf6ivar/dfn` contains multiple files with
these entries. See `modflow6/doc/mf6io/mf6ivar/readme.md` for details.

The files are read, converted to dictionaries  and dumped as JSON.
The files have the form `gwf-evt.dfn` and `gwf-buy.dfn`.
Here we use the terminology category and package for the name parts.

The output lands in `resources/mf6_var_names` and has the form
`<tag>/<category>/<package>.json`

# Memory Manager Variables


"""

import json
import os
from pathlib import Path
from subprocess import run
import sys

import pymf6

MF6_CODE_DIR = Path().home() / 'Dev/modflow6'
MF6_SOURCE_DIR = MF6_CODE_DIR / 'src'
MF6_INPUT_VAR_DIR = MF6_CODE_DIR / 'doc/mf6io/mf6ivar'
MF6_MEM_VAR_FILE = MF6_INPUT_VAR_DIR / 'md' / 'mf6memvar.md'
OUT_DIR = (Path(pymf6.__file__).parent / 'resources/mf6_var_names').absolute()
OUT_DIR_INPUT = OUT_DIR / 'input_vars'
OUT_DIR_MEM_VARS = OUT_DIR / 'mem_vars'



class VersionTag:
    """Context manager for a version tag.

    This switches to the tag position with `git switch --detach <tag>`
    in `__enter__`and back to `develop in `__exit__`
    """

    def __init__(
            self,
            tag,
            mf6_var_dir=MF6_INPUT_VAR_DIR,
            out_dir=OUT_DIR_INPUT):
        assert len([int(entry) for entry in tag.split('.')]) == 3
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


def _write_input_var_docs(file_name, var_docs, out_dir):
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


def save_input_var_docs(tag):
    """Save MF6 input_variable documentation to JSON files."""
    with VersionTag(tag) as version_tag:
        for file_name in os.listdir(version_tag.dfn_dir):
            file_path = version_tag.dfn_dir / file_name
            mf6_vars = version_tag.mf6ivar.parse_mf6var_file(file_path)
            var_docs = {key[0]: value for key, value in mf6_vars.items()}
            var_docs = _make_description(var_docs, mf6ivar=version_tag.mf6ivar)
            _write_input_var_docs(
                file_name=file_name,
                var_docs=var_docs,
                out_dir=version_tag.out_dir_tag)




def read_mem_vars(mem_var_path=MF6_MEM_VAR_FILE):
    """Read names of memory manager Varibles"""

    def split_line(line):
        """Split a markdowm table line.

        Format:
        | name 1 | name 2| name 3 |
        """
        return [value for entry in line.split('|') if (value := entry.strip())]

    with open(mem_var_path, encoding='utf-8') as fobj:
        for line in fobj:
            if line.strip().startswith('|'):
                header = split_line(line)
                break
        next(fobj)
        mem_vars = {head: [] for head in header}
        for line in fobj:
            for head, value in zip(header, split_line(line)):
                mem_vars[head].append(value)
    return mem_vars


def make_mem_var_names(mem_vars=MF6_MEM_VAR_FILE):
    """Create MF6 varible names."""
    header = list(mem_vars.keys())
    keys = [name for name in header if name != 'variable name']
    mem_var_names = {}
    for pos, name in enumerate(mem_vars['variable name']):
        name = name.upper()
        values = {}
        for key in keys:
            values[key] = mem_vars[key][pos]
        mem_var_names.setdefault(name, []).append(values)
    return mem_var_names


def add_docs(docs, path):
    """Add docstrings to `docs`."""

    def shorten_path(path):
        """Cut of path elements before `src`."""
        parts = path.parts
        pos = parts.index('src')
        return str(Path(*parts[pos:]))

    with open(path, encoding='utf-8') as fobj:
        for line_no, line in enumerate(fobj, 1):
            if '::' in line and '!' in line:
                name = line.split('::')[1].split()[0].upper()
                doc = line.split('!')[-1].split('<')[-1].strip()
                if name in docs:
                    name_data = docs[name]
                else:
                    name_data = {}
                name_data.setdefault(doc, []).append(
                    {'source_file': shorten_path(path),
                      'line_no': line_no}
                      )
                docs[name] = name_data


def read_mem_var_docs(src_path=MF6_SOURCE_DIR):
    """Read docstrings from Fortran files."""
    docs = {}
    for root, _, files in os.walk(src_path):
        for file in files:
            path = Path(root) / file
            add_docs(docs, path)
    return docs


def save_mem_var_docs(tag, out_dir=OUT_DIR_MEM_VARS):
    """Save docstrings into a JSON file."""
    with VersionTag(tag) :
        mem_vars = read_mem_vars()
        mem_var_names = make_mem_var_names(mem_vars)
        docs = read_mem_var_docs()
    no_docs = mem_var_names.keys() - docs.keys()
    extra_docs = docs.keys() - mem_var_names.keys()
    out_sub_dir = out_dir / tag
    out_sub_dir.mkdir(exist_ok=True)
    with open(out_sub_dir / 'mem_var_docs.json', 'w', encoding='utf-8') as fobj:
        json.dump(docs, fobj)
    Path(out_sub_dir / 'no_docs.txt').write_text(
        '\n'.join(sorted(no_docs)) +  '\n',
        encoding='utf-8')
    Path(out_sub_dir / 'extra_docs.txt').write_text(
        '\n'.join(sorted(extra_docs)) +  '\n',
        encoding='utf-8')


if __name__ == '__main__':
    # save_input_var_docs('6.4.1')
    save_mem_var_docs('6.4.1')
