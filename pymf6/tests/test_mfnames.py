"""
Test getting names from MODFLOW 6 *.lst file
"""

from pymf6.mfnames import get_names


def test_get_names():
    """Test getting MF6 of name-origin pairs"""
    get_names(verbose=True, show_mf6_output=True)
    get_names(force_generate=True, verbose=True, show_mf6_output=True)
    get_names(verbose=True)


if __name__ == '__main__':
    test_get_names()
