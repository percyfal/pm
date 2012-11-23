"""wrapper interface class"""
import os

from cement.core import interface, handler


class ConfigDefaults(dict):
    """Represent a config defaults section for wrappers"""
    def __init__(self, **kw):
        self.opts = kw.get("opts", None) # Program options as a string
        

def wrapper_interface_validator(cls, obj):
    members = [
        'cl', 
        'cmd_args',
        'version',
        'group',
        'label'
        ]
    interface.validate(IWrapper, obj, members)

# Notes
#
# The config_defaults section is a (interfaced?) dictionary that goes
# to the configuration file. It should among other things contain
# - opts
# - label
#
# What is the order to load? In setup, do
# _setup_program_config_handler or the like, reading the .pm2 config,
# overriding the (sensible) config defaults. Then, if a command is
# passed that uses a project directory, look for appropriately named
# config file in that directory and override defaults. This must then
# be done "post-setup" - or in "_pre_dispatch"?

class IWrapper(interface.Interface):
    
    class IMeta:
        """Interface meta-data"""
        group = 'group'
        """The string identifier for the wrapper group"""
        label = 'wrapper'
        """The string identifier of the interface"""
        validator = wrapper_interface_validator
        """The interface validator function."""
        in_ext = []
        """Input file extensions"""
        out_ext = []
        """Output file extensions"""
        ext_map = {}
        """mapping from input file extension to output file extension"""
        path = None
        """Path to command"""
        exe = None
        """Base executable"""
        cmd_args = []
        """Command argument list"""
        command_template = None
        """Command template"""
        config_defaults = ConfigDefaults()
        
    Meta = interface.Attribute("Handler Meta-data")

    def _setup(app_obj):
        """
        The _setup function is called during application initialization and
        must 'setup' the handler object making it ready for the framework
        or the application to make further calls to it.
        
        :param app_obj: The application object. 
        """

    def cl(indata=None, outdata=None, **kw):
        """
        Generate command as string

        """

    def cmd_args(indata=None, outdata=None, **kw):
        """
        Generate command as list

        """

    def version():
        """
        Get program version
        """

class BaseWrapper(handler.CementBaseHandler):
    """
    Base class that all Wrappers should sub-class from.
    """
    __name__ = "__name__"
    __module__ = "__module__"

    class Meta:
        """Handler meta-data"""
        label = None

        interface = IWrapper
        
        exe = ""

        version = None

        

    def __init__(self, *args, **kw):
        super(BaseWrapper, self).__init__(*args, **kw)

    def __str__(self):
        return str(self.cl())

    def __repr__(self):
        return "{}".format(self.__class__)

    def version(self):
        return self._meta.version

    def cl(self):
        return " ".join(self.cmd_args())

    def cmd_args(self):
        return [self._meta.exe]

class JavaConfigDefaults(ConfigDefaults):
    """Configuration defaults for java programs"""
    def __init__(self, **kw):
        super(JavaConfigDefaults, self).__init__(**kw)
        self.memory = kw.get("memory", "3g")
        self.opts = kw.get("opts", 'VALIDATION_STRINGENCY=SILENT')

class JavaMixin(object):
    """Mixin for java based programs"""
    class Meta:
        exe = 'java'
        """Program"""

        jarfile = None
        """Jar file"""

        config_label = 'java'
        """Label in configuration dictionary"""

        config_defaults = JavaConfigDefaults(opts="oeu")
        """Default java configuration"""

        cmd_args = [exe, '-jar', config_defaults["opts"]]
        """Command arguments"""

    def __init__(self):
        super(JavaMixin, self).__init__()
