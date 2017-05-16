"""byte-apsw - executor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.apsw.tasks import ApswSelectTask
from byte.executors.core.base import ExecutorPlugin
from byte.queries import SelectQuery

import apsw
import os


class ApswExecutor(ExecutorPlugin):
    """APSW executor class."""

    key = 'apsw'

    class Meta(ExecutorPlugin.Meta):
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

    def __init__(self, collection, model):
        """Create APSW executor.

        :param collection: Collection
        :type collection: byte.collection.Collection

        :param model: Model
        :type model: byte.model.Model
        """
        super(ApswExecutor, self).__init__(collection, model)

        self.connection = None

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

    def connect(self):
        """Connect to database.

        :return: APSW Connection
        :rtype: apsw.Connection
        """
        if self.connection:
            return self.connection

        # Connect to database
        self.connection = apsw.Connection(self.path)

        # Enable write-ahead logging
        self.connection.cursor().execute('PRAGMA journal_mode=WAL;')

        return self.connection

    def cursor(self):
        """Create database cursor.

        :return: APSW Cursor
        :rtype: apsw.Cursor
        """
        return self.connect().cursor()

    def transaction(self):
        """Create database transaction.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        return self.connect()

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

        raise NotImplementedError('Unsupported query: %s' % (type(query).__name__,))
