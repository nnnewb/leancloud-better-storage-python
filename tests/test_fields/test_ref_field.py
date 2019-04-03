import pytest

from leancloud_better_storage.storage.fields import RefField, Field
from leancloud_better_storage.storage.models import Model


@pytest.fixture(scope='function', autouse=True)
def model_cls():
    class Person(Model):
        name = Field()
        age = Field()
        gender = Field()
        sweet_heart = RefField(ref_cls='Person')

    Person.clear()

    yield Person

    Person.clear()


def test_initialize_ref_field(model_cls):
    girl = model_cls.create()
    boy = model_cls.create(sweet_heart=girl.lc_object)
    girl.commit()
    boy.commit()
    assert isinstance(boy.sweet_heart, model_cls)
    assert boy.sweet_heart.object_id == girl.object_id


def test_assign_ref_field(model_cls):
    girl = model_cls.create()
    boy = model_cls.create()
    boy.sweet_heart = girl

    assert isinstance(boy.sweet_heart, model_cls)
    assert boy.sweet_heart.object_id == girl.object_id

    boy.sweet_heart = None
    boy.sweet_heart = girl.lc_object

    assert isinstance(boy.sweet_heart, model_cls)
    assert boy.sweet_heart.object_id == girl.object_id


def test_get_null_ref_field(model_cls):
    girl = model_cls.create()
    boy = model_cls.create()
    girl.commit()
    boy.commit()
    assert boy.sweet_heart is None
    assert girl.sweet_heart is None


def test_get_included_ref_field(model_cls):
    girl = model_cls.create()
    boy = model_cls.create(sweet_heart=girl.lc_object)
    girl.commit()
    boy.commit()

    result = model_cls.query().filter_by(object_id=boy.object_id).includes(model_cls.sweet_heart).first()
    assert result.sweet_heart.object_id == girl.object_id


def test_get_not_included_ref_field(model_cls):
    model_cls.sweet_heart.lazy = False
    girl = model_cls.create(name='alice')
    boy = model_cls.create(sweet_heart=girl.lc_object)
    girl.commit()
    boy.commit()

    result = model_cls.query().filter_by(object_id=boy.object_id).first()
    assert result.sweet_heart.object_id == girl.object_id
    assert result.sweet_heart.name is None


def test_get_not_included_lazy_load_ref_field(model_cls):
    girl = model_cls.create(name='alice')
    boy = model_cls.create(sweet_heart=girl.lc_object)
    girl.commit()
    boy.commit()

    result = model_cls.query().filter_by(object_id=boy.object_id).first()
    assert result.sweet_heart.object_id == girl.object_id
    assert result.sweet_heart.name == girl.name
