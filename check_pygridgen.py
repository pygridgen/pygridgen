import sys
import matplotlib
from matplotlib import style

matplotlib.use('agg')
style.use('classic')

import pygridgen  # noqa: E402

if '--strict' in sys.argv:
    sys.argv.remove('--strict')
    status = pygridgen.teststrict(*sys.argv[1:])
else:
    status = pygridgen.test(*sys.argv[1:])

sys.exit(status)
