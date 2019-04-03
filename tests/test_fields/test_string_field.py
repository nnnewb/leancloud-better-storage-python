import pytest

from leancloud_better_storage.storage.fields import StringField
from leancloud_better_storage.storage.models import Model


@pytest.fixture()
def model_cls():
    class Person(Model):
        name = StringField(max_length=8)

    Person.clear()

    yield Person

    Person.clear()


def test_break_maximum_when_assign(model_cls):
    man = model_cls.create(name='1234')
    with pytest.raises(ValueError):
        man.name = '123456789'  # too long


def test_break_maximum_when_create(model_cls):
    with pytest.raises(ValueError):
        model_cls.create(name='123456789')  # too long


def test_contains(model_cls):
    inst = model_cls.create(name='remilia scarlet')
    inst.commit()
    inst = model_cls.create(name='flandre scarlet')
    inst.commit()
    inst = model_cls.create(name='hakurei reimu')
    inst.commit()
    results = model_cls.query().filter(model_cls.name.contains('scarlet')).find()
    names = [i.name for i in results]
    assert 'hakurei reimu' not in names
    assert 'flandre scarlet' in names
    assert 'remilia scarlet' in names


def test_startswith(model_cls):
    inst = model_cls.create(name='remilia scarlet')
    inst.commit()
    inst = model_cls.create(name='flandre scarlet')
    inst.commit()
    inst = model_cls.create(name='hakurei reimu')
    inst.commit()
    results = model_cls.query().filter(model_cls.name.startswith('hakurei')).find()
    names = [i.name for i in results]
    assert 'hakurei reimu' in names
    assert 'flandre scarlet' not in names
    assert 'remilia scarlet' not in names


def test_regex(model_cls):
    inst = model_cls.create(name='remilia scarlet')
    inst.commit()
    inst = model_cls.create(name='flandre scarlet')
    inst.commit()
    inst = model_cls.create(name='hakurei reimu')
    inst.commit()
    results = model_cls.query().filter(model_cls.name.regex(r'.*kurei.*')).find()
    names = [i.name for i in results]
    assert 'hakurei reimu' in names
    assert 'flandre scarlet' not in names
    assert 'remilia scarlet' not in names
