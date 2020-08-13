"""Context manager for temporay directory
"""

import os


class TempDir:
    """Switch to a temporary directory and back.

    This is a context manager.
    """

    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self.orig_dir = None

    def __enter__(self):
        self.orig_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def __exit__(self, *args):
        os.chdir(self.orig_dir)
