"""pm configuration settings"""

import os
from cement.core import backend

config_defaults = backend.defaults('log', 'programs', 'projects')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.getenv("HOME"), "log", "pm.log")
config_defaults['programs'] = {}
config_defaults['programs']['gatk'] = {'test':1, 'opt':"my option string"}
