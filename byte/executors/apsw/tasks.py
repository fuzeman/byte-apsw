"""byte-apsw - executor tasks module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Task, ReadTask, SelectTask, WriteTask


class ApswTask(Task):
    """APSW task base class."""

    def __init__(self, executor, statements):
        """Create APSW executor task.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param statements: SQLite Statements
        :type statements: list of (str, tuple)
        """
        super(ApswTask, self).__init__(executor)

        self.statements = statements

        self.cursor = None

    def open(self):
        """Open task."""
        self.cursor = self.executor.cursor()

    def execute(self):
        """Execute task."""
        self.open()

        # Execute statements inside transaction
        with self.executor.transaction():
            for operation in self.statements:
                if not isinstance(operation, tuple) or len(operation) != 2:
                    raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

                print('EXECUTE: %r %r' % operation)
                self.cursor.execute(*operation)

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
