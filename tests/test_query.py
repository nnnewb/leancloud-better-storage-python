from unittest import TestCase

import leancloud

from better_leancloud_storage.storage import models, fields

from .utils import setup


class TestModelQuery(TestCase):

    def setUp(self):
        setup()
        self.cls_name = 'TestModel'

        class ModelA(models.Model):
            __lc_cls__ = self.cls_name

            name = fields.Field()
            age = fields.Field()

        self.Model = ModelA

        self.models = [
            self.Model.create(name='Hi', age=18),
            self.Model.create(name='Ho', age=21),
            self.Model.create(name='He', age=23),
        ]
        for model in self.models:
            model.commit()

    def tearDown(self):
        try:
            while True:
                result = leancloud.Query(self.cls_name).find()
                if len(result) == 0:
                    break
                leancloud.Object.destroy_all(result)
        except leancloud.LeanCloudError:
            pass

    def test_query_by_equation(self):
        model = self.Model.query().filter_by(name='Hi').first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

    def test_query_by_less_than(self):
        model = self.Model.query().filter(self.Model.age < 19).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

    def test_query_by_less_than_or_equal_to(self):
        model = self.Model.query().filter(self.Model.age <= 18).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

        results = self.Model.query().filter(self.Model.age <= 21).find()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertLessEqual(result.age, 21)

    def test_query_by_greater_than(self):
        model = self.Model.query().filter(self.Model.age > 22).first()
        self.assertEqual(model.name, 'He')
        self.assertEqual(model.age, 23)

    def test_query_by_greater_than_or_equal_to(self):
        model = self.Model.query().filter(self.Model.age >= 23).first()
        self.assertEqual(model.name, 'He')
        self.assertEqual(model.age, 23)

        results = self.Model.query().filter(self.Model.age >= 21).find()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertGreaterEqual(result.age, 21)

    def test_no_conditions(self):
        results = self.Model.query().find()
        self.assertEqual(len(results), 3)