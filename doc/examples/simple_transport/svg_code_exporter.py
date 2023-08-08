"""Export Python code in SVG format."""

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import SvgFormatter


def export_code_as_svg(code, file_name='code.svg'):
    """Export Python code in SVG format."""
    with open(file_name, 'w', encoding='utf8') as fobj:
        fobj.write(highlight(code, PythonLexer(), SvgFormatter()))
