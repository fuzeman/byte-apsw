"""byte-apsw - executor tasks module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Task, ReadTask, SelectTask, WriteTask


class ApswTask(Task):
    """APSW task base class."""

    def __init__(self, executor, sql, parameters):
        """Create APSW executor task.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param sql: SQLite Statement
        :type sql: str

        :param parameters: SQLite Parameters
        :type parameters: tuple
        """
        super(ApswTask, self).__init__(executor)

        self.sql = sql
        self.parameters = parameters

        self.cursor = None

    def open(self):
        """Open task."""
        self.cursor = self.executor.cursor()

    def execute(self):
        """Execute task."""
        self.open()

        # Execute SQL
        print('EXECUTE: %r %r' % (self.sql, self.parameters))
        self.cursor.execute(self.sql, self.parameters)

        return self

    def close(self):
        """Close task."""
        self.cursor.close()


class ApswReadTask(ReadTask, ApswTask):
    """APSW read task class."""

    pass


class ApswSelectTask(SelectTask, ApswReadTask):
    """APSW select task class."""

    def items(self):
        """Retrieve items from task."""
        for row in self.cursor:
            yield self.model.from_plain(
                self._build_item(row),
                translate=True
            )

    def _build_item(self, row):
        data = {}

        for i, (c_name, c_type) in enumerate(self.cursor.getdescription()):
            data[c_name] = row[i]

        return data


class ApswWriteTask(WriteTask, ApswTask):
    """APSW write task class."""

    pass
