"""pm configuration settings"""

import os
from cement.core import backend

config_defaults = backend.defaults('log')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.getenv("HOME"), "log", "pm.log")

