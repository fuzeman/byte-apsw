from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.model import Model
from byte.property import Property
import byte.compilers.sqlite
import byte.executors.apsw


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_all():
    """Test all items can be retrieved from database."""
    users = Collection(User, 'apsw://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.apsw
    ])

    # Create table, and add items directly to database
    users.executor.connect().cursor().execute("""
        CREATE TABLE users (
            id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
            username    VARCHAR(255),
            password    VARCHAR(255)
        );

        INSERT INTO users (username, password) VALUES
            ('one', 'alpha'),
            ('two', 'beta'),
            ('three', 'charlie');
    """)

    # Validate items
    assert [(i.username, i.password) for i in users.all()] == [
        ('one',     'alpha'),
        ('two',     'beta'),
        ('three',   'charlie')
    ]
