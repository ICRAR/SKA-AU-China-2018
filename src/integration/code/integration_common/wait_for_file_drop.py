"""
Wait for a file to appear from
"""
import logging
from os import listdir
from time import sleep

from dlg.drop import BarrierAppDROP

LOGGER = logging.getLogger(__name__)


class WaitForFile(BarrierAppDROP):
    def __init__(self, oid, uid, **kwargs):
        self._root_directory = None
        self._directory_to_check = None
        self._starts_with = None
        super(WaitForFile, self).__init__(oid, uid, **kwargs)

    def initialize(self, **kwargs):
        super(WaitForFile, self).initialize(**kwargs)
        self._root_directory = self._getArg(kwargs, 'root_directory', None)
        self._starts_with = self._getArg(kwargs, 'starts_with', None)

    def run(self):
        for file in reversed(sorted(listdir(self._root_directory))):
            LOGGER.info('Looking at {}'.format(file))
            if file.startswith('dlg_work_dir_'):
                LOGGER.info('Found {}'.format(file))
                self._directory_to_check = file
                break

        LOGGER.info('Looking in {}'.format(self._directory_to_check))
        found = False
        while not found:
            sleep(5)
            for file in listdir(self._directory_to_check):
                if file.startswith(self._starts_with):
                    found = True
                    break

    def dataURL(self):
        return 'WaitForFile'
