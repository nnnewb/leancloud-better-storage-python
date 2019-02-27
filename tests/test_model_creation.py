from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models, fields
from tests.utils import setup


class TestModelCreation(TestCase):

    def setUp(self):
        self.cls_name = 'TestModel'
        self.cls_names = [self.cls_name, 'TestModelA', 'TestModelB']
        setup()

    def tearDown(self):
        for cls_name in self.cls_names:
            try:
                leancloud.Object.destroy_all(leancloud.Query(cls_name).find())
            except leancloud.LeanCloudError:
                pass

    def test_simple_create(self):
        class PersonA(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        instance = PersonA.create(name='my name')
        self.assertEqual(instance.lc_object.get('name'), 'my name')

        class PersonB(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field('NameField')

        instance = PersonB.create(name='my name')
        self.assertEqual(instance.lc_object.get('NameField'), 'my name')

    def test_create_miss_required(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field(nullable=False)

        with self.assertRaises(KeyError):
            Person.create()

    def test_create_unknown_field(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name

        with self.assertRaises(KeyError):
            Person.create(name='123')

    def test_simple_create_inherit(self):
        class BaseModel(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        class PersonA(BaseModel):
            __lc_cls__ = self.cls_names[1]
            age = fields.Field()

        class PersonB(BaseModel):
            __lc_cls__ = self.cls_names[2]

        person_a = PersonA.create(name='1')
        person_b = PersonA.create(name='2', age=10)
        person_c = PersonB.create(name='3')

        self.assertEqual(person_a.lc_object.get('name'), '1')
        self.assertEqual(person_b.lc_object.get('name'), '2')
        self.assertEqual(person_b.lc_object.get('age'), 10)
        self.assertEqual(person_c.lc_object.get('name'), '3')

    def test_simple_commit(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        person = Person.create(name='Hello world')
        person.commit()
        self.assertEqual(person.name, 'Hello world')

    def test_bulk_commit(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        persons = [
            Person.create(name='Hi {0}'.format(i))
            for i in range(10)
        ]
        Person.commit_all(*persons)

    def test_create_with_default(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field(nullable=False, default='Hi')

        person = Person.create()
        self.assertEqual(person.name, 'Hi')
        person.commit_all()
        person.drop()

    def test_create_with_default_initializer(self):
        class Person(models.Model):
            __lc_cls__ = 'TestModel'
            name = models.Field(default=lambda: '12345')

        person = Person.create()
        self.assertEqual(person.name, '12345')

    def test_create_named_field_with_default(self):
        class Person(models.Model):
            __lc_cls__ = self.cls_name
            other_name = models.Field('name', default='Hello')

        person = Person.create()
        self.assertEqual(person.other_name, 'Hello')
        self.assertEqual(Person.__fields__['other_name'].field_name, 'name')
        person.commit()
        person.drop()

    def test_initialize_field_with_undefined(self):
        class PersonA(models.Model):
            __lc_cls__ = self.cls_names[1]
            undefined_initialized_field = models.Field()

        class PersonB(models.Model):
            __lc_cls__ = self.cls_names[2]
            none_initialized_field = models.Field(default=None)

        m = PersonA.create()
        m.commit()
        assert 'undefined_initialized_field' not in m.lc_object._attributes
        assert m.undefined_initialized_field is None

        m2 = PersonB.create()
        m2.commit()
        assert 'none_initialized_field' in m2.lc_object._attributes
        assert m2.none_initialized_field is None
