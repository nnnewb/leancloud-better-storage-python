from unittest import TestCase

import leancloud

from leancloud_better_storage.storage.fields import DateTimeField
from leancloud_better_storage.storage.models import Model


class TestDateTimeField(TestCase):

    def setUp(self):
        self.cls_name = 'FieldTypeTest'

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