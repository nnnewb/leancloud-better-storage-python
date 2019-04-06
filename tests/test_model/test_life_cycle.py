from unittest import TestCase

import leancloud

from leancloud_better_storage.storage.fields import Field
from leancloud_better_storage.storage.models import Model


class TestLifeCycleHook(TestCase):

    def setUp(self):
        self.cls_name = 'FieldTypeTest'

    def tearDown(self):
        try:
            leancloud.Object.destroy_all(leancloud.Query(self.cls_name).find())
        except leancloud.LeanCloudError:
            pass

    def test_created_hook(self):

        class Created(Exception):
            pass

        def fn(instance):
            raise Created()

        class M(Model):
            field = Field()

        M.register_pre_create_hook(fn)
        instance = M.create()
        with self.assertRaises(Created):
            instance.commit()

    def test_updated_hook(self):

        class Updated(Exception):
            pass

        def fn(instance):
            raise Updated()

        class M(Model):
            field = Field()

        M.register_pre_update_hook(fn)
        instance = M.create()
        instance.commit()
        with self.assertRaises(Updated):
            instance.commit()

    def test_deleted_hook(self):

        class Deleted(Exception):
            pass

        def fn(instance):
            raise Deleted()

        class M(Model):
            field = Field()

        M.register_pre_delete_hook(fn)
        instance = M.create()
        instance.commit()
        with self.assertRaises(Deleted):
            instance.drop()

    def test_declared_callback(self):
        class AfterModelCreated(Exception):
            pass

        class CustomField(Field):

            def _after_model_created(self, model, name):
                super(CustomField, self)._after_model_created(model, name)
                raise AfterModelCreated()

        with self.assertRaises(AfterModelCreated):
            class Person(Model):
                a = CustomField()

    def test_inherit_created_hook(self):
        class Created(Exception):
            pass

        def fn(instance):
            raise Created()

        class Base(Model):
            pass

        Base.register_pre_create_hook(fn)

        class M(Base):
            field = Field()

        instance = M.create()
        with self.assertRaises(Created):
            instance.commit()

    def test_inherit_updated_hook(self):
        class Updated(Exception):
            pass

        def fn(instance):
            raise Updated()

        class Base(Model):
            pass

        Base.register_pre_update_hook(fn)

        class M(Base):
            field = Field()

        instance = M.create()
        instance.commit()
        with self.assertRaises(Updated):
            instance.commit()

    def test_inherit_deleted_hook(self):
        class Deleted(Exception):
            pass

        def fn(instance):
            raise Deleted()

        class Base(Model):
            pass

        Base.register_pre_delete_hook(fn)

        class M(Base):
            field = Field()

        instance = M.create()
        instance.commit()
        with self.assertRaises(Deleted):
            instance.drop()
