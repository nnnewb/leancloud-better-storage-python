import os

import leancloud
import pytest

from leancloud_better_storage.storage.models import Model


@pytest.fixture(scope='session', autouse=True)
def leancloud_init():
    app_id = os.getenv('LEANCLOUD_APP_ID')
    app_key = os.getenv('LEANCLOUD_APP_KEY')
    master_key = os.getenv('LEANCLOUD_MASTER_KEY', None)
    leancloud.init(app_id, app_key, master_key)


@pytest.fixture(scope='session', autouse=True)
def mock():
    def clear(cls: Model):
        """
        :type cls: Model
        :param cls:
        :return:
        """
        while True:
            results = cls.query().find()
            if len(results) == 0:
                break
            cls.drop_all(*results)

    Model.clear = classmethod(clear)
