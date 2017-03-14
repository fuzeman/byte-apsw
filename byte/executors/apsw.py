from __future__ import absolute_import

from byte.compilers.sqlite import SqliteCompiler
from byte.executors.base import Executor
from byte.statements import StatementResult
import apsw
import os


class ApswExecutor(Executor):
    def __init__(self, collection, model):
        super(ApswExecutor, self).__init__(collection, model)

        self.compiler = SqliteCompiler(collection, model)

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

    def execute(self, query):
        sql, parameters = self.compiler.compile(query)

        if not sql:
            raise ValueError('Empty query')

        print('EXECUTE: %r %r' % (sql, parameters))

        cursor = self.cursor().execute(sql, parameters)

        # TODO Check cursor state?

        return ApswStatementResult(
            self.collection,
            self.model,
            cursor
        )


class ApswStatementResult(StatementResult):
    def __init__(self, collection, model, cursor):
        super(ApswStatementResult, self).__init__(collection, model)

        self.cursor = cursor

    def iterator(self):
        for row in self.cursor:
            yield self.model.from_plain(
                self._map_row(row),
                translate=True
            )

    def _map_row(self, row):
        data = {}

        for i, (c_name, c_type) in enumerate(self.cursor.getdescription()):
            data[c_name] = row[i]

        return data

    def __iter__(self):
        return self.iterator()