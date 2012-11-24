"""Gatk wrappers"""
import os
import pm.wrappers as wrap

class GATKBaseWrapper(wrap.JavaMixin, wrap.BaseWrapper):
    """
    This class is an implementation of the :ref:`IWrapper
    <pm.wrappers>` interface.
    """
    class Meta:
        """Handler meta-data"""
        interface = wrap.IWrapper
        label = 'gatk'
        group = 'gatk'
        path = os.getenv("GATK_HOME")

    def cl(self, input_file=None, output_file=None):
        print "Cmd args " + str(self._meta.cmd_args)
        return " ".join(self._meta.cmd_args)

class GATKCalculateHsMetricsWrapper(GATKBaseWrapper):
    """
    This class is an implementation of the :ref:`IWrapper
    <pm.wrappers>` interface.
    """
    class Meta:
        """Handler meta-data"""
        label = 'calculate_hs_metrics'

    def cl(self, input_file=None, output_file=None):
        print "Cmd args " + str(self._meta.cmd_args)
        print "Cmd args " + str(self.cmd_args())
        return " ".join(self._meta.cmd_args)
