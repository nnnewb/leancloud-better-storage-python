from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models, fields

from tests.utils import setup


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
        while True:
            result = leancloud.Query(self.cls_name).find()
            if len(result) == 0:
                break
            leancloud.Object.destroy_all(result)

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

    def test_query_by_less_and_greater(self):
        result = self.Model.query().filter(self.Model.age > 18).and_().filter(self.Model.age < 23).find()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age, 21)
        self.assertEqual(result[0].name, 'Ho')

    def test_query_by_less_or_greater(self):
        result = self.Model.query().filter(self.Model.age < 21).or_().filter(self.Model.age > 21).find()
        self.assertEqual(len(result), 2)
        result = sorted(result, key=lambda model: model.age)
        self.assertEqual(result[0].age, 18)
        self.assertEqual(result[0].name, 'Hi')
        self.assertEqual(result[1].age, 23)
        self.assertEqual(result[1].name, 'He')

    def test_query_by_not_equal(self):
        result = self.Model.query().filter(self.Model.age != 21).find()
        self.assertEqual(len(result), 2)

    def test_query_single_field_multi_condition(self):
        result = self.Model.query().filter(self.Model.age != 21, self.Model.age != 18).find()
        self.assertEqual(len(result), 1)

    def test_query_by_contains(self):
        model = self.Model.query().filter(self.Model.name.contains('i')).first()
        self.assertEqual(model.name, 'Hi')
        model = self.Model.query().filter(self.Model.name.contains('o')).first()
        self.assertEqual(model.name, 'Ho')
        model = self.Model.query().filter(self.Model.name.contains('e')).first()
        self.assertEqual(model.name, 'He')

        self.assertEqual(len(self.Model.query().filter(self.Model.name.contains('i')).find()), 1)
        self.assertEqual(len(self.Model.query().filter(self.Model.name.contains('o')).find()), 1)
        self.assertEqual(len(self.Model.query().filter(self.Model.name.contains('e')).find()), 1)

    def test_no_conditions(self):
        results = self.Model.query().find()
        self.assertEqual(len(results), 3)

    def test_count(self):
        self.assertEqual(self.Model.query().count(), 3)

    def test_sort_result_order_by_ascending(self):
        model = self.Model.query().order_by(self.Model.age.asc).first()
        self.assertEqual(model.age, 18)
        self.assertEqual(model.name, 'Hi')

    def test_sort_result_order_by_descending(self):
        model = self.Model.query().order_by(self.Model.age.desc).first()
        self.assertEqual(model.age, 23)
        self.assertEqual(model.name, 'He')

    def test_condition_in(self):
        model = self.Model.query().filter(self.Model.name.in_(['Hi', 'hi', 'HI'])).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

        model = self.Model.query().filter(self.Model.name.in_(['Hii', 'hii', 'HII'])).first()
        self.assertIsNone(model)
