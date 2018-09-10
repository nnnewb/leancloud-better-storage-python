from unittest import TestCase
from uuid import uuid1

import leancloud

from leancloud_better_storage.storage import models, fields
from tests.utils import setup


class TestModelCreation(TestCase):

    def setUp(self):
        self.cls_name = 'TestModel'
        setup()

    def tearDown(self):
        try:
            leancloud.Object.destroy_all(leancloud.Query(self.cls_name).find())
        except leancloud.LeanCloudError:
            pass

    def test_simple_create(self):
        class MyModel(models.Model):
            name = fields.Field()

        instance = MyModel.create(name='my name')
        self.assertEqual(instance.lc_object.get('name'), 'my name')

        class ModelB(models.Model):
            name = fields.Field('NameField')

        instance = ModelB.create(name='my name')
        self.assertEqual(instance.lc_object.get('NameField'), 'my name')

    def test_create_miss_required(self):
        class ModelA(models.Model):
            name = fields.Field(nullable=False)

        try:
            ModelA.create()
            raise Exception('Missing required field should raise a KeyError!')
        except KeyError:
            pass

    def test_create_unknown_field(self):
        class ModelA(models.Model):
            pass

        try:
            ModelA.create(name='123')
            raise Exception('Unknown field in creation should raise a KeyError!')
        except KeyError:
            pass

    def test_simple_create_inherit(self):
        class BaseModel(models.Model):
            name = fields.Field()

        class ModelA(BaseModel):
            age = fields.Field()

        class ModelB(BaseModel):
            pass

        a = ModelA.create(name='1')
        b = ModelA.create(name='2', age=10)
        c = ModelB.create(name='3')

        self.assertEqual(a.lc_object.get('name'), '1')
        self.assertEqual(b.lc_object.get('name'), '2')
        self.assertEqual(b.lc_object.get('age'), 10)
        self.assertEqual(c.lc_object.get('name'), '3')

    def test_simple_commit(self):
        class ModelA(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        a = ModelA.create(name='Hello world')
        a.commit()
        self.assertEqual(a.name, 'Hello world')

    def test_bulk_commit(self):
        class ModelA(models.Model):
            __lc_cls__ = self.cls_name
            name = fields.Field()

        instances = [
            ModelA.create(name='Hi {0}'.format(i))
            for i in range(10)
        ]
        ModelA.commit_all(*instances)

    def test_create_with_default(self):
        class ModelA(models.Model):
            __lc_cls__ = self.cls_name

            name = fields.Field(nullable=False, default='Hi')

        model = ModelA.create()
        self.assertEqual(model.name, 'Hi')
        model.commit_all()
        model.drop()

    def test_create_with_default_initializer(self):
        class MyModel(models.Model):
            __lc_cls__ = 'TestModel'

            name = models.Field(default=lambda: '12345')

        model = MyModel.create()
        self.assertEqual(model.name, '12345')

    def test_create_named_field_with_default(self):
        class MyModel(models.Model):
            hi = models.Field('name', default='Hello')

        model = MyModel.create()
        model.commit()
        model.drop()
