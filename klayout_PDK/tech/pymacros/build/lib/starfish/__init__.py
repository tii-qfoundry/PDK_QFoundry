import sys

from ._version import __version__
if hasattr(sys.modules[__name__], "_version"):
    del _version  # remove to avoid confusion with __version__

