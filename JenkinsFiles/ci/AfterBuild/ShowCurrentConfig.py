import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config

Config.print_all_config()
