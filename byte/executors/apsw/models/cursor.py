"""byte-apsw - executor cursor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseCursor

import logging

log = logging.getLogger(__name__)


class ApswCursor(DatabaseCursor):
    """APSW cursor class."""

    def __init__(self, executor, connection=None):
        """Create APSW Cursor.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param connection: Connection
        :type connection: byte.executors.apsw.models.connection.ApswConnection or None
        """
        super(ApswCursor, self).__init__(executor, connection=connection)

        # Create cursor
        self.instance = self.connection.instance.cursor()

    @property
    def columns(self):
        """Retrieve columns description from cursor."""
        return self.instance.description

    def execute(self, statement, parameters=None):
        """Execute statement."""
        log.debug('Execute: %r %r', statement, parameters)

        if not parameters:
            return self.instance.execute(statement)

        return self.instance.execute(statement, parameters)

    def close(self):
        """Close cursor."""
        super(ApswCursor, self).close()

        # Close cursor
        self.instance.close()
        self.instance = None

    def __iter__(self):
        return iter(self.instance)
