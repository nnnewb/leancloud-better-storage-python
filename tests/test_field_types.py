from unittest import TestCase

import leancloud
from leancloud import GeoPoint

from leancloud_better_storage.storage.fields import GeoPointField
from leancloud_better_storage.storage.models import Model
from tests.utils import setup


class TestFieldTypes(TestCase):

    def setUp(self):
        self.cls_name = 'FieldTypeTest'
        setup()

    def tearDown(self):
        try:
            leancloud.Object.destroy_all(leancloud.Query(self.cls_name).find())
        except leancloud.LeanCloudError:
            pass

    def test_initialize_geo_point_field(self):
        class M(Model):
            __lc_cls__ = self.cls_name
            geo = GeoPointField()

        m = M.create(geo=GeoPoint(30, 30))
        m.commit()
        m = M.query().filter_by(object_id=m.object_id).first()
        self.assertEqual(type(m.geo), GeoPoint)
