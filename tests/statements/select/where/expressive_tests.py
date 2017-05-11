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


def test_equals():
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
        
        INSERT INTO users (id, username, password) VALUES
            (1, 'one', 'alpha'),
            (2, 'two', 'beta'),
            (3, 'three', 'charlie');
    """)

    # Validate items
    user = users.select().where(User['username'] == 'one').first()

    assert user is not None
    assert user.username == 'one'
    assert user.password == 'alpha'


def test_not_equals():
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
        
        INSERT INTO users (id, username, password) VALUES
            (1, 'one', 'alpha'),
            (2, 'two', 'beta'),
            (3, 'three', 'charlie');
    """)

    # Validate items
    users = list(users.select().where(User['username'] != 'two').execute())

    assert len(users) == 2
