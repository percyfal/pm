"""Gatk wrappers"""
import os
import pm.wrappers as wrap

class GATKWrapper(wrap.BaseWrapper, wrap.JavaMixin):
    """
    This class is an implementation of the :ref:`IWrapper
    <pm.wrappers>` interface.
    """
    class Meta:
        """Handler meta-data"""
        interface = wrap.IWrapper
        label = 'gatk'
        path = os.getenv("GATK_HOME")

    def version(self):
        return ""

    def cl(self, input_file=None, output_file=None):
        return " ".join(self._meta.cmd_args)
