import sys
sys.dont_write_bytecode = True

import sharedlib
from mdxlib import MDXlib

try:
    import SAM
except ImportError:
    pass
try:
    import FEA
except ImportError:
    pass
try:
    import TEALL
except ImportError:
    pass
try:
    import TE1by1
except ImportError:
    pass

