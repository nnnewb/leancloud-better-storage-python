from unittest import TestCase
from better_leancloud_storage.storage import models, fields


class TestModelCreation(TestCase):

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
