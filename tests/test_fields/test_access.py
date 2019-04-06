from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models, fields


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
            name = fields.Field()

        model = ModelA.create(name='my name')
        self.assertEqual(model.name, 'my name')

    def test_inherit_field_access(self):
        class BaseModel(models.Model):
            name = fields.Field()

        class ModelA(BaseModel):
            pass

        class ModelB(BaseModel):
            age = fields.Field()

        a = ModelA.create(name='my name')
        self.assertEqual(a.name, 'my name')
        b = ModelB.create(name='my name', age=18)
        self.assertEqual(b.name, 'my name')
        self.assertEqual(b.age, 18)

    def test_multi_inherit_overwrite_field(self):
        class BaseA(models.Model):
            name = fields.Field()

        class BaseB(models.Model):
            name = fields.Field()

        class ModelA(BaseA):
            name = fields.Field()

        class ModelB(BaseA, BaseB):
            name = fields.Field()

        class ModelC(BaseA, BaseB):
            age = fields.Field()

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
            name = fields.Field()

        model = ModelA.create(name='hi')
        model.commit()
        self.assertEqual(model.name, 'hi')
        model.name = 'ho'
        model.commit()
        self.assertEqual(model.name, 'ho')
