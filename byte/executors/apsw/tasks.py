"""byte-apsw - executor tasks module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Task, ReadTask, SelectTask, WriteTask

import logging

log = logging.getLogger(__name__)


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


class ApswReadTask(ReadTask, ApswTask):
    """APSW read task class."""

    def __init__(self, executor, statements):
        """Create APSW read task.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param statements: SQLite Statements
        :type statements: list of (str, tuple)
        """
        super(ApswReadTask, self).__init__(executor, statements)

        self.cursor = self.executor.cursor()

    def execute(self):
        """Execute task."""
        for operation in self.statements:
            if not isinstance(operation, tuple) or len(operation) != 2:
                raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

            self.cursor.execute(*operation)

        return self

    def close(self):
        """Close task."""
        self.cursor.close()


class ApswSelectTask(SelectTask, ApswReadTask):
    """APSW select task class."""

    def items(self):
        """Retrieve items from task."""
        # Parse items from cursor
        for row in self.cursor:
            yield self.model.from_plain(
                self._build_item(row),
                translate=True
            )

        # Close cursor
        self.close()

    def _build_item(self, row):
        data = {}

        for i, column in enumerate(self.cursor.columns):
            data[column[0]] = row[i]

        return data


class ApswWriteTask(WriteTask, ApswTask):
    """APSW write task class."""

    def __init__(self, executor, statements):
        """Create APSW write task.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param statements: SQLite Statements
        :type statements: list of (str, tuple)
        """
        super(ApswWriteTask, self).__init__(executor, statements)

        # Retrieve transaction
        self.transaction = self.executor.transaction()

    def execute(self):
        """Execute task."""
        with self.transaction:
            for operation in self.statements:
                if not isinstance(operation, tuple) or len(operation) != 2:
                    raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

                self.transaction.execute(*operation)

        return self

    def close(self):
        """Close task."""
        pass


class ApswInsertTask(ApswWriteTask):
    """APSW insert task class."""

    pass
