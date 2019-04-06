import leancloud
import pytest

from leancloud_better_storage.storage.models import Model


@pytest.fixture(scope='module')
def fill_table():
    leancloud.use_master_key()

    class Person(Model):
        pass

    Person.clear()

    rest = []
    for _ in range(100):
        rest.append(Person.create())

    Person.commit_all(*rest)

    yield

    Person.clear()


def test_scan(fill_table):
    class Person(Model):
        pass

    assert isinstance(Person.query().scan().lc_cursor, leancloud.query.Cursor)
    results = [*Person.query().scan()]
    assert len(results) == 100
