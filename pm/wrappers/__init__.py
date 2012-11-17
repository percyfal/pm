"""wrapper interface class"""
import os

from cement.core import interface, handler

def wrapper_interface_validator(cls, obj):
    members = [
        'cl', 
        'cmd_args',
        'version',
        ]
    interface.validate(IWrapper, obj, members)

class IWrapper(interface.Interface):
    
    class IMeta:
        """Interface meta-data"""
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
        opts = ""
        """Program options as string"""

        

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

    class Meta:
        """Handler meta-data"""
        label = None

        interface = IWrapper
        
        exe = ""

    def __init__(self, *args, **kw):
        super(BaseWrapper, self).__init__(*args, **kw)

    def __str__(self):
        return str(self.cl())

    def __repr__(self):
        return "{}".format(self.__class__)

    def version(self):
        return None

    def cl(self):
        return " ".join(self.cmd_args())

    def cmd_args(self):
        return [self._meta.exe]

class JavaMixin(object):
    """Mixin for java based programs"""
    class Meta:
        opts = 'VALIDATION_STRINGENCY=SILENT '
        """Java program options"""

        memory = '3g'
        """Java memory"""

        exe = 'java'
        """Program"""

        jarfile = None
        """Jar file"""

        cmd_args = [exe, '-jar', opts]
        """Command arguments"""

    def __init__(self):
        super(JavaMixin, self).__init__()
