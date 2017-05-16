from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.model import Model
from byte.property import Property
import byte.compilers.sqlite
import byte.executors.apsw

from apsw import ConstraintError
from contextlib import closing
from hamcrest import *
import pytest


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_single():
    """Test multiple items are inserted inside a transaction."""
    users = Collection(User, 'apsw://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.apsw
    ])

    # Create table
    with closing(users.executor.connect().cursor()) as cursor:
        with users.executor.connect():
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

    # Try insert items with conflict
    with pytest.raises(ConstraintError):
        users.insert().items(
            {'id': 1, 'username': 'one', 'password': 'alpha'},
            {'id': 2, 'username': 'two', 'password': 'beta'},
            {'id': 1, 'username': 'one', 'password': 'charlie'},
            {'id': 3, 'username': 'three', 'password': 'delta'}
        ).execute()

    # Ensure no items were inserted
    assert_that(list(users.all()), has_length(0))
