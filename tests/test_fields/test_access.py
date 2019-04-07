from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models
from leancloud_better_storage.storage.fields import Field


class TestAccess(TestCase):

    def setUp(self):
        self.cls_name = 'TestModel'

    def tearDown(self):
        while True:
            result = leancloud.Query(self.cls_name).find()
            if len(result) == 0:
                break
            leancloud.Object.destroy_all(result)

    def test_simple_access(self):
        class ModelA(models.Model):
            name = Field()

        model = ModelA.create(name='my name')
        self.assertEqual(model.name, 'my name')

    def test_inherit_field_access(self):
        class BaseModel(models.Model):
            name = Field()

        class ModelA(BaseModel):
            pass

        class ModelB(BaseModel):
            age = Field()

        a = ModelA.create(name='my name')
        self.assertEqual(a.name, 'my name')
        b = ModelB.create(name='my name', age=18)
        self.assertEqual(b.name, 'my name')
        self.assertEqual(b.age, 18)

    def test_multi_inherit_overwrite_field(self):
        class BaseA(models.Model):
            name = Field()

        class BaseB(models.Model):
            name = Field()

        class ModelA(BaseA):
            name = Field()

        class ModelB(BaseA, BaseB):
            name = Field()

        class ModelC(BaseA, BaseB):
            age = Field()

        a = ModelA.create(name='hello')
        self.assertEqual(a.name, 'hello')
        b = ModelB.create(name='world')
        self.assertEqual(b.name, 'world')
        c = ModelC.create(name='!', age=10)
        self.assertEqual(c.name, '!')
        self.assertEqual(c.age, 10)

    def test_commit_change(self):
        class ModelA(models.Model):
            __lc_cls__ = self.cls_name
            name = Field()

        model = ModelA.create(name='hi')
        model.commit()
        self.assertEqual(model.name, 'hi')
        model.name = 'ho'
        model.commit()
        self.assertEqual(model.name, 'ho')
