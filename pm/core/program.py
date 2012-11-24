"""pm core programs module."""

from cement.core import exc, backend as cement_backend
from pm.core import backend
import pm.wrappers as wrap

LOG = cement_backend.minimal_logger(__name__)

def _define(group, name):
    """
    Define a program namespace that plugins can register programs in.
    
    :param group: The name of the program group, stored as programs['group']
    :param name: The name of the program, stored as programs['group']['name']
    :raises: cement.core.exc.FrameworkError
    """
    LOG.debug("defining program group '{}', program name '{}'".format(group,name))
    if group not in backend.programs:
        backend.programs[group] = {}
    if name in backend.programs[group]:
        raise exc.FrameworkError("Program name '{}' already defined in group '{}'!".format(name, group))
    backend.programs[group][name] = None
 
def defined(group, program_name=None):
    """
    Test whether a program group and possibly program name is defined.
    
    :param group: The name of the program group. 
    :param program_name: The name of the program. 
    :returns: True if the program is defined, False otherwise.
    :rtype: boolean
    
    """
    if not group in backend.programs:
        return False
    if not program_name:
        return True
    if program_name in backend.programs[group]:
        return True
    else:
        return False   
    
def register(wrapper):
    """
    Register a program wrapper.

    :param wrapper: The IWrapper function to register to the program
    group name. This is an *un-instantiated* class.

    Usage:
    
    .. code-block:: python
        
        import pm.wrappers as wrap
        from pm.core import program
        
        class MyProgramWrapper(*args, **kwargs):
            class Meta:
                interface = wrap.IWrapper
                group = 'MyPrograms'
                label = 'myprogram'
                path = os.getenv("MYPROGRAM")
                exe = "myprogram"
                VERSION = 1.0

            def cl(self, input_file=None, output_file=None, *args, **kw):
                return " ".join(self._meta.cmd_args)
    
        programs.register(MyProgramWrapper)
        
    """
    if not isinstance(wrapper, wrap.BaseWrapper):
        raise exc.FrameworkError("Can only register BaseWrapper objects. Received '{}'!".format(type(wrapper)))

    if defined(wrapper._meta.group, wrapper._meta.label):
        LOG.debug("program name '{}' in group '{}' already defined! ignoring...".format(wrapper._meta.group, wrapper._meta.label))
        return False
        
    LOG.debug("registering program name '{}' from {} into programs['{}']['{}']" % \
                  (wrapper.__name__, wrapper.__module__, wrapper._meta.group, wrapper._meta.label))

    _define(wrapper._meta.group, wrapper._meta.label)
    backend.programs[wrapper._meta.group][wrapper._meta.label] = wrapper
