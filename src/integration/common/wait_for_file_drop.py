"""
Wait for a file to appear from
"""
from os import listdir
from time import sleep

from dlg.drop import BarrierAppDROP


class WaitForFile(BarrierAppDROP):
    def __init__(self, oid, uid, **kwargs):
        self._root_directory = None
        self._directory_to_check = None
        super(WaitForFile, self).__init__(oid, uid, **kwargs)

    def initialize(self, **kwargs):
        super(WaitForFile, self).initialize(**kwargs)
        self._root_directory = self._getArg(kwargs, 'root_directory', None)

        work_dirs = []
        for file in listdir(self._root_directory):
            if file.startswith('dlg_work_dir_'):
                work_dirs.append(file)
        work_dirs = reversed(sorted(work_dirs))
        self._directory_to_check = work_dirs[0]

    def run(self):
        found = False
        while not found:
            sleep(5)
            for file in listdir(self._directory_to_check):
                if file.startswith('ngas-file-'):
                    found = True
                    break

    def dataURL(self):
        return 'WaitForFile'
