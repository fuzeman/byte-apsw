"""byte-apsw - executor transaction module."""
from __future__ import absolute_import, division, print_function

from byte.executors.apsw.models.cursor import ApswCursor
from byte.executors.core.models.database import DatabaseTransaction


class ApswTransaction(DatabaseTransaction, ApswCursor):
    """APSW transaction class."""

    def begin(self):
        """Begin transaction."""
        self.instance.execute('BEGIN;')

    def commit(self):
        """Commit transaction."""
        self.instance.execute('COMMIT;')

    def rollback(self):
        """Rollback transaction."""
        self.instance.execute('ROLLBACK;')

    def close(self):
        """Close transaction."""
        # Close transaction
        super(ApswTransaction, self).close()

        # Close cursor
        self.instance.close()
        self.instance = None
