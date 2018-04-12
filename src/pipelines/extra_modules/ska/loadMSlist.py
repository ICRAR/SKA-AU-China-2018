import os,logging
from dlg.drop import BarrierAppDROP

logger = logging.getLogger(__name__)

class LoadMSlistApp(BarrierAppDROP):

    def initialize(self, **kwargs):
        super(LoadMSlistApp, self).initialize(**kwargs)

    def run(self):
        self._filePath = self.inputs[0].path#self._getArg(kwargs, 'Arg01', None)#MSLIST
        if (not os.path.exists(self._filePath)):
            raise Exception("MSlist file %s does not existed" % self._filePath)

        if len(self.outputs) < 1:
            raise Exception("at least one output is expected by this application")

        i = 0
        with open(self._filePath, 'rb') as f :
            lines = f.readlines()
            for line in lines:
                if not line :
                    continue
                if i >= len(self.outputs):
                    i = 0
                self.outputs[i].write(line)
                i = i + 1
