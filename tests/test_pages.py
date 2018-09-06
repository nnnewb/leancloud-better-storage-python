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
            self.Model.create(name='Hi {0}'.format(i), age=18)
            for i in range(100)
        ]
        self.Model.commit_all(*self.models)

    def tearDown(self):
        try:
            while True:
                result = leancloud.Query(self.cls_name).find()
                if len(result) == 0:
                    break
                leancloud.Object.destroy_all(result)
        except leancloud.LeanCloudError:
            pass

    def test_one_page(self):
        pages = self.Model.query().paginate(0, 100)
        c = 0
        for p in pages:
            c += len(p.items)

        self.assertEqual(c, 100)

    def test_ten_pages(self):
        pages = self.Model.query().paginate(0, 10)
        c = 0
        ca = 0
        for p in pages:
            c += 1
            ca += len(p.items)
        self.assertEqual(c, 10)
