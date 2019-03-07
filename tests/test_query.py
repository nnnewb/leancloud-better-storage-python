from unittest import TestCase

import leancloud

from leancloud_better_storage.storage import models, fields
from leancloud_better_storage.storage.query import QueryLogicalError
from tests.utils import setup


class TestModelQuery(TestCase):

    def setUp(self):
        setup()

        class People(models.Model):
            __lc_cls__ = 'TEST_People'

            name = fields.Field()
            age = fields.Field()
            profile = fields.Field()

        class PeopleProfile(models.Model):
            __lc_cls__ = 'TEST_PeopleProfile'

            score = fields.Field()

        self.People = People
        self.PeopleProfile = PeopleProfile

        self.models = [
            self.People.create(name='Hi', age=18),
            self.People.create(name='Ho', age=21),
            self.People.create(name='He', age=23),
        ]
        for model in self.models:
            model.commit()

    def tearDown(self):
        for clsname in ('TEST_People', 'TEST_PeopleProfile'):
            while True:
                result = leancloud.Query(clsname).find()
                if len(result) == 0:
                    break
                leancloud.Object.destroy_all(result)

    def test_query_by_equation(self):
        model = self.People.query().filter_by(name='Hi').first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

    def test_query_by_less_than(self):
        model = self.People.query().filter(self.People.age < 19).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

    def test_query_by_less_than_or_equal_to(self):
        model = self.People.query().filter(self.People.age <= 18).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

        results = self.People.query().filter(self.People.age <= 21).find()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertLessEqual(result.age, 21)

    def test_query_by_greater_than(self):
        model = self.People.query().filter(self.People.age > 22).first()
        self.assertEqual(model.name, 'He')
        self.assertEqual(model.age, 23)

    def test_query_by_greater_than_or_equal_to(self):
        model = self.People.query().filter(self.People.age >= 23).first()
        self.assertEqual(model.name, 'He')
        self.assertEqual(model.age, 23)

        results = self.People.query().filter(self.People.age >= 21).find()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertGreaterEqual(result.age, 21)

    def test_query_by_less_and_greater(self):
        result = self.People.query().filter(self.People.age > 18).and_().filter(self.People.age < 23).find()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age, 21)
        self.assertEqual(result[0].name, 'Ho')

    def test_query_by_less_or_greater(self):
        result = self.People.query().filter(self.People.age < 21).or_().filter(self.People.age > 21).find()
        self.assertEqual(len(result), 2)
        result = sorted(result, key=lambda model: model.age)
        self.assertEqual(result[0].age, 18)
        self.assertEqual(result[0].name, 'Hi')
        self.assertEqual(result[1].age, 23)
        self.assertEqual(result[1].name, 'He')

    def test_query_by_not_equal(self):
        result = self.People.query().filter(self.People.age != 21).find()
        self.assertEqual(len(result), 2)

    def test_query_single_field_multi_condition(self):
        result = self.People.query().filter(self.People.age != 21, self.People.age != 18).find()
        self.assertEqual(len(result), 1)

    def test_query_by_contains(self):
        model = self.People.query().filter(self.People.name.contains('i')).first()
        self.assertEqual(model.name, 'Hi')
        model = self.People.query().filter(self.People.name.contains('o')).first()
        self.assertEqual(model.name, 'Ho')
        model = self.People.query().filter(self.People.name.contains('e')).first()
        self.assertEqual(model.name, 'He')

        self.assertEqual(len(self.People.query().filter(self.People.name.contains('i')).find()), 1)
        self.assertEqual(len(self.People.query().filter(self.People.name.contains('o')).find()), 1)
        self.assertEqual(len(self.People.query().filter(self.People.name.contains('e')).find()), 1)

    def test_no_conditions(self):
        results = self.People.query().find()
        self.assertEqual(len(results), 3)

    def test_count(self):
        self.assertEqual(self.People.query().count(), 3)

    def test_sort_result_order_by_ascending(self):
        model = self.People.query().order_by(self.People.age.asc).first()
        self.assertEqual(model.age, 18)
        self.assertEqual(model.name, 'Hi')

    def test_sort_result_order_by_descending(self):
        model = self.People.query().order_by(self.People.age.desc).first()
        self.assertEqual(model.age, 23)
        self.assertEqual(model.name, 'He')

    def test_condition_in(self):
        model = self.People.query().filter(self.People.name.in_(['Hi', 'hi', 'HI'])).first()
        self.assertEqual(model.name, 'Hi')
        self.assertEqual(model.age, 18)

        model = self.People.query().filter(self.People.name.in_(['Hii', 'hii', 'HII'])).first()
        self.assertIsNone(model)

    def test_startswith_condition(self):
        model = self.People.create(name='iH', age=81)
        model.commit()

        results = self.People.query().filter(self.People.name.startswith('H')).find()
        for result in results:
            self.assertIn(result.name, ('Hi', 'Ho', 'He'))

    def test_regex_condition(self):
        model = self.People.create(name='iH', age=81)
        model.commit()

        results = self.People.query().filter(self.People.name.regex('i$')).find()
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertEqual(result.name, 'Hi')
            self.assertEqual(result.age, 18)

    def test_query_with_includes(self):
        profile = self.PeopleProfile.create(score=100)
        profile.commit()

        people = self.People.query().filter_by(name='Hi').first()
        people.profile = profile.lc_object
        people.commit()

        result = self.People.query().filter_by(object_id=people.object_id).includes(self.People.profile).first()
        self.assertEqual(result.profile.get('score'), 100)

        people = self.People.query().filter_by(name='Ho').includes(self.People.profile).first()
        self.assertIsNone(people.profile)

        people = self.People.query().filter_by(name='Hi').first()
        self.assertIsNone(people.profile.get('score'))

    def test_invalid_connected_logical_ops(self):
        class People(models.Model):
            name = models.Field()

        with self.assertRaises(QueryLogicalError):
            People.query().filter_by(name='123').and_().and_().first()
        with self.assertRaises(QueryLogicalError):
            People.query().filter_by(name='123').and_().or_().first()
        with self.assertRaises(QueryLogicalError):
            People.query().filter_by(name='123').or_().or_().first()
