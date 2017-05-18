"""byte-apsw - executor connection module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseConnection


class ApswConnection(DatabaseConnection):
    """APSW connection class."""

    def __init__(self, executor, instance):
        """Create apsw connection.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param instance: APSW Connection
        :type instance: apsw.Connection
        """
        super(ApswConnection, self).__init__(executor)

        self.instance = instance
