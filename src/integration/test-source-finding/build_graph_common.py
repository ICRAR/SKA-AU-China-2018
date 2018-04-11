"""

"""

import getpass
import logging
import time
from abc import ABCMeta, abstractmethod

from dlg.apps.bash_shell_app import BashShellApp
from dlg.drop import dropdict, BarrierAppDROP

LOGGER = logging.getLogger(__name__)


def get_module_name(item):
    return item.__module__ + '.' + item.__name__


class AbstractBuildGraph:
    # This ensures that:
    #  - This class cannot be instantiated
    #  - Subclasses implement methods decorated with @abstractmethod
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self._drop_list = []
        self._session_id = self.get_session_id()
        self._counters = {}

    @property
    def drop_list(self):
        return self._drop_list

    @property
    def session_id(self):
        return self._session_id

    def add_drop(self, drop):
        self._drop_list.append(drop)

    def get_oid(self, count_type):
        count = self._counters.get(count_type)
        if count is None:
            count = 1
        else:
            count += 1
        self._counters[count_type] = count

        return '{0}__{1:06d}'.format(count_type, count)

    def create_memory_drop(self, node_id, oid='memory_drop'):
        oid_text = self.get_oid(oid)
        # uid_text = self.get_uuid()
        drop = dropdict({
            "type": 'plain',
            "storage": 'memory',
            "oid": oid_text,
            # "uid": uid_text,
            "precious": False,
            "node": node_id,
        })
        self.add_drop(drop)
        return drop

    def create_bash_shell_app(self, node_id, command, oid='bash_shell_app', input_error_threshold=100):
        oid_text = self.get_oid(oid)
        # uid_text = self.get_uuid()
        drop = dropdict({
            "type": 'app',
            "app": get_module_name(BashShellApp),
            "oid": oid_text,
            # "uid": uid_text,
            "command": command,
            "input_error_threshold": input_error_threshold,
            "node": node_id,
        })
        self.add_drop(drop)
        return drop

    def create_barrier_app(self, node_id, oid='barrier_app', input_error_threshold=100):
        oid_text = self.get_oid(oid)
        # uid_text = self.get_uuid()
        drop = dropdict({
            "type": 'app',
            "app": get_module_name(BarrierAppDROP),
            "oid": oid_text,
            # "uid": uid_text,
            "input_error_threshold": input_error_threshold,
            "node": node_id,
        })
        self.add_drop(drop)
        return drop

    @staticmethod
    def get_session_id():
        return '{0}-{1}'.format(
            getpass.getuser(),
            time.strftime('%Y%m%d%H%M%S')
        )

    @abstractmethod
    def build(self):
        """
        Build the graph
        """
