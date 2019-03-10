import leancloud

from leancloud_better_storage.storage._util import cache_result


class ObjectId:

    def __init__(self, object_id, model_cls):
        self._model_cls = model_cls
        self._id = object_id

    @property
    def id(self):
        return self._id

    @property
    @cache_result('self._leancloud_object')
    def lc_object(self):
        return leancloud.Object.create_without_data(self.id)

    def fetch(self):
        return self._model_cls(self.lc_object.fetch())

    def __eq__(self, other):
        assert isinstance(other, ObjectId)
        return self.id == other.id

    def __ne__(self, other):
        assert isinstance(other, ObjectId)
        return self.id
