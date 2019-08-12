"""
Formatters for `__repr__` and `_repr_html_` for some data structures.
"""

import numpy as np

np.set_printoptions(threshold=30)


def format_text_table(data):
    """Format a list of dicts as text table"""

    def ljust_line(data):
        """
        Left justify list elements and add `|` separators.
        :param data: List of strings
        :return: Line string
        """
        sep = ' | '
        left = '| '
        right = ' |\n'
        values = (entry.ljust(width) for entry, width in
                  zip(data, col_widths))
        return left + sep.join(values) + right

    col_widths = [0] * len(data[0])
    for elem in data:
        for index, value in enumerate(elem.values()):
            col_widths[index] = max(col_widths[index], len(value))
    for index, value in enumerate(data[0].keys()):
        col_widths[index] = max(col_widths[index], len(value))

    total_width = sum(col_widths) + len(col_widths) * 4 - 2
    double_line = '=' * total_width + '\n'
    single_line = '-' * total_width + '\n'
    text_repr = double_line
    text_repr += ljust_line(data[0].keys())
    text_repr += single_line
    for elem in data:
        text_repr += ljust_line(elem.values())
    text_repr += double_line
    return text_repr


def format_html_table(data):
    """Format a list of dicts as HTML table"""
    html_repr = """<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">"""

    head = """<thead>
                 <tr style="text-align: right;">\n"""
    for name in data[0].keys():
        head += f'<th>{name}</th>\n'
    head += """</tr>
  </thead>
"""
    body = """<tbody>"""
    for model in data:
        body += '<tr>\n'
        for value in model.values():
            body += f'<td>{value}</td>\n'
        body += '</tr>\n'
    body += """</tbody>"""
    html_repr += head
    html_repr += body
    html_repr += """
</table>
</div>"""
    return html_repr


def make_repr(obj):
    """
    Make a representation text
    :param obj: Python object
    :return: representation text
    """
    repr_text = f'{obj.__class__.__name__} {obj.name} '
    if hasattr(obj, 'package_names'):
        repr_text += f'\n{len(obj.package_names)} packages'
    if hasattr(obj, 'var_names'):
        repr_text += f'\n{len(obj.var_names)} variables.'
    if hasattr(obj, 'value'):
        repr_text += f'\nvalue: {repr(obj.value)}'
        if obj.value.shape:
            repr_text += f'\nshape: {obj.value.shape}'
    if hasattr(obj, 'origin'):
        repr_text += f'\nlocation: {obj.origin}'
    return repr_text


def make_repr_html(obj):
    """
    Make a nice HTML table
    :param obj: Python object
    :return: HTML string
    """
    html_text = f'<h3>{obj.__class__.__name__} {obj.name}</h3>'
    html_text += '<table><tbody>'
    if hasattr(obj, 'package_names'):
        html_text += '<tr><td>number of packages:</td>'
        html_text += f'<td>{len(obj.package_names)}</td></tr>'
    if hasattr(obj, 'var_names'):
        html_text += '<tr><td>number of variables: </td>'
        html_text += f'<td>{len(obj.var_names)}</td></tr>'
    if hasattr(obj, 'value'):
        html_text += '<tr><td>value: </td>'
        html_text += f'<td>{repr(obj.value)}</td></tr>'
        if obj.value.shape:
            html_text += '<tr><td>shape: </td>'
            html_text += f'<td>{obj.value.shape}</td></tr>'
    if hasattr(obj, 'origin'):
        html_text += '<tr><td>location: </td>'
        html_text += f'<td>{obj.origin}</td></tr>'
    html_text += '</tbody></table>'
    return html_text
