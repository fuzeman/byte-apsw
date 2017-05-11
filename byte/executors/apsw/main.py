from __future__ import absolute_import, division, print_function

from byte.executors.core.base import ExecutorPlugin
from byte.statements import SelectStatement
from byte.executors.apsw.tasks import ApswSelectTask
import apsw
import os


class ApswExecutor(ExecutorPlugin):
    key = 'apsw'

    class Meta(ExecutorPlugin.Meta):
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
        super(ApswExecutor, self).__init__(collection, model)

        self.connection = None

    @property
    def path(self):
        path = (
            self.collection.uri.netloc +
            self.collection.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        return self.plugins.get_compiler('sqlite')(self)

    def connect(self):
        if self.connection:
            return self.connection

        # Connect to database
        self.connection = apsw.Connection(self.path)

        # Enable write-ahead logging
        self.connection.cursor().execute('PRAGMA journal_mode=WAL;')

        return self.connection

    def cursor(self):
        return self.connect().cursor()

    def execute(self, statement):
        sql, parameters = self.compiler.compile(statement)

        if not sql:
            raise ValueError('Empty statement')

        # Construct task
        if isinstance(statement, SelectStatement):
            return ApswSelectTask(self, sql, parameters).execute()

        raise NotImplementedError('Unsupported statement: %s' % (type(statement).__name__,))
