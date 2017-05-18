"""byte-apsw - executor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.apsw.models.connection import ApswConnection
from byte.executors.apsw.models.cursor import ApswCursor
from byte.executors.apsw.models.transaction import ApswTransaction
from byte.executors.apsw.tasks import ApswInsertTask, ApswSelectTask
from byte.executors.core.base import DatabaseExecutorPlugin
from byte.queries import InsertQuery, SelectQuery

import apsw
import logging
import os

log = logging.getLogger(__name__)


class ApswExecutor(DatabaseExecutorPlugin):
    """APSW executor class."""

    key = 'apsw'

    class Meta(DatabaseExecutorPlugin.Meta):
        """APSW executor metadata."""

        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

        scheme = [
            'apsw',
            'sqlite'
        ]

    @property
    def path(self):
        """Retrieve database path.

        :return: Database Path
        :rtype: str
        """
        path = (
            self.collection.uri.netloc +
            self.collection.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        # Parse version string
        version_info = tuple([
            int(value)
            for value in apsw.sqlitelibversion().split('.')
        ])

        # Construct compiler
        return self.plugins.get_compiler('sqlite')(
            self,
            version=version_info
        )

    def create_connection(self):
        """Connect to database.

        :return: APSW Connection
        :rtype: apsw.Connection
        """
        # Connect to database
        instance = apsw.Connection(self.path)

        # Create connection
        connection = ApswConnection(self, instance)

        # Configure connection
        with connection.transaction() as transaction:
            # Enable write-ahead logging
            transaction.execute('PRAGMA journal_mode=WAL;')

        return connection

    def create_transaction(self, connection=None):
        """Create database transaction.

        :return: APSW Connection
        :rtype: apsw.Connection
        """
        return ApswTransaction(
            self,
            connection=connection
        )

    def cursor(self, connection=None):
        """Create database cursor.

        :return: Cursor
        :rtype: byte.executors.apsw.models.cursor.ApswCursor
        """
        return ApswCursor(
            self,
            connection=connection
        )

    def execute(self, query):
        """Execute query.

        :param query: Query
        :type query: byte.queries.Query
        """
        statements = self.compiler.compile(query)

        if not statements:
            raise ValueError('No statements returned from compiler')

        # Construct task
        if isinstance(query, SelectQuery):
            return ApswSelectTask(self, statements).execute()

        if isinstance(query, InsertQuery):
            return ApswInsertTask(self, statements).execute()

        raise NotImplementedError('Unsupported query: %s' % (type(query).__name__,))
