from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models, fields


class TestDrop(TestCase):

    def setUp(self):
        self.cls_name = 'TestModel'

        class Person(models.Model):
            __lc_cls__ = self.cls_name

            name = fields.Field()
            age = fields.Field()

        self.Model = Person

    def tearDown(self):
        while True:
            result = leancloud.Query(self.cls_name).find()
            if len(result) == 0:
                break
            leancloud.Object.destroy_all(result)

    def test_drop_without_exception(self):
        model = self.Model.create(name='Hello', age=10)
        model.commit()
        model.drop()
        self.assertIsNone(model.lc_object)
        model = self.Model.query().filter_by(name='Hello').first()
        self.assertIsNone(model)

    def test_drop_all_without_exception(self):
        models = [
            self.Model.create(name='Hi {0}'.format(i), age=18)
            for i in range(10)
        ]
        for model in models:
            model.commit()

        self.Model.drop_all(*models)
        for instance in models:
            self.assertIsNone(instance.lc_object)

        model = self.Model.query().filter_by(name='Hi 1').first()
        self.assertIsNone(model)
