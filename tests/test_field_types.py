from unittest import TestCase

import leancloud

from leancloud_better_storage.storage.fields import RefField, Field, DateTimeField
from leancloud_better_storage.storage.models import Model
from tests.utils import setup


class TestRefField(TestCase):

    def setUp(self):
        self.cls_name = 'FieldTypeTest'
        setup()

    def tearDown(self):
        try:
            leancloud.Object.destroy_all(leancloud.Query(self.cls_name).find())
        except leancloud.LeanCloudError:
            pass

    def test_initialize_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            girl_friend = RefField(ref_cls='Person')

        girl = Person.create()
        boy = Person.create(girl_friend=girl.lc_object)
        girl.commit()
        boy.commit()
        self.assertIsInstance(boy.girl_friend, Person)
        self.assertEqual(boy.girl_friend.object_id, girl.object_id)

    def test_assign_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            girl_friend = RefField(ref_cls='Person')

        girl = Person.create()
        boy = Person.create()
        boy.girl_friend = girl

        self.assertIsInstance(boy.girl_friend, Person)
        self.assertEqual(boy.girl_friend.object_id, girl.object_id)

        boy.girl_friend = None
        boy.girl_friend = girl.lc_object

        self.assertIsInstance(boy.girl_friend, Person)
        self.assertEqual(boy.girl_friend.object_id, girl.object_id)

    def test_get_null_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            girl_friend = RefField(ref_cls='Person')

        girl = Person.create()
        boy = Person.create()
        girl.commit()
        boy.commit()
        self.assertIsNone(boy.girl_friend)
        self.assertIsNone(girl.girl_friend)

    def test_get_included_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            girl_friend = RefField(ref_cls='Person')

        girl = Person.create()
        boy = Person.create(girl_friend=girl.lc_object)
        girl.commit()
        boy.commit()

        result = Person.query().filter_by(object_id=boy.object_id).includes(Person.girl_friend).first()
        self.assertEqual(result.girl_friend.object_id, girl.object_id)

    def test_get_not_included_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            name = Field()
            girl_friend = RefField(ref_cls='Person', lazy=False)

        girl = Person.create(name='alice')
        boy = Person.create(girl_friend=girl.lc_object)
        girl.commit()
        boy.commit()

        result = Person.query().filter_by(object_id=boy.object_id).first()
        self.assertEqual(result.girl_friend.object_id, girl.object_id)
        self.assertIsNone(result.girl_friend.name)

    def test_get_not_included_lazy_load_ref_field(self):
        class Person(Model):
            __lc_cls__ = self.cls_name
            name = Field()
            girl_friend = RefField(ref_cls='Person', lazy=True)

        girl = Person.create(name='alice')
        boy = Person.create(girl_friend=girl.lc_object)
        girl.commit()
        boy.commit()

        result = Person.query().filter_by(object_id=boy.object_id).first()
        self.assertEqual(result.girl_friend.object_id, girl.object_id)
        self.assertEqual(result.girl_friend.name, girl.name)


class TestDateTimeField(TestCase):

    def setUp(self):
        self.cls_name = 'FieldTypeTest'
        setup()

    def tearDown(self):
        try:
            leancloud.Object.destroy_all(leancloud.Query(self.cls_name).find())
        except leancloud.LeanCloudError:
            pass

    def test_auto_fill_created_at(self):
        """ test auto fill field such as created_at. """

        class M(Model):
            __lc_cls__ = self.cls_name

        instance = M.create()
        instance.commit()
        self.assertIsNotNone(instance.created_at)

    def test_auto_now_add(self):
        class M(Model):
            __lc_cls__ = self.cls_name

            birthday = DateTimeField(auto_now_add=True)

        instance = M.create()
        instance.commit()
        self.assertIsNotNone(instance.birthday)

    def test_auto_now(self):
        class M(Model):
            __lc_cls__ = self.cls_name

            birthday = DateTimeField(auto_now=True)

        instance = M.create()
        instance.commit()
        self.assertIsNone(instance.birthday)
        instance.commit()
        self.assertIsNotNone(instance.birthday)
