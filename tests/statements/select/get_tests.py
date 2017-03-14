from byte import Collection, Model, Property, List


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_simple():
    users = Collection(User, 'apsw://:memory:?table=users')

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
    user = users.get(2)

    assert user is not None
    assert user.username == 'two'
    assert user.password == 'beta'
