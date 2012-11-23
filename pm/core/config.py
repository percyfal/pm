"""pm configuration settings"""

import os
from cement.core import backend

# Top-level configurations
config_defaults = backend.defaults('log', 'projects', 'programs')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.getenv("HOME"), "log", "pm.log")

# Program configurations
program_config_defaults = backend.defaults('programs')
program_config_defaults['gatk'] = {'test':1, 'opt':"my option string"}
