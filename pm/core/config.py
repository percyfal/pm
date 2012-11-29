"""pm configuration settings"""

import os
from cement.core import backend

# Top-level configurations
config_defaults = backend.defaults('log', 'projects', 'programs', 'config')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.getenv("HOME"), "log", "pm.log")

# Project and sample default configuration files
config_defaults['config']['project'] = os.path.join(os.getenv("HOME"), ".pm2", "projects.yaml")
config_defaults['config']['sample'] = os.path.join("config", "samples.yaml")

# Program configurations
program_config_defaults = backend.defaults('programs')
program_config_defaults['gatk'] = {'test':1, 'opt':"my option string"}
