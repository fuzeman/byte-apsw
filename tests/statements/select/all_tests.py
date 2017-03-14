from byte import Collection, Model, Property, List


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_all():
    users = Collection(User, 'apsw://:memory:?table=users')

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
