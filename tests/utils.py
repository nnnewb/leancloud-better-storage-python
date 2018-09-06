import os
import sys

import leancloud


def setup():
    app_id = os.getenv('LEANCLOUD_APP_ID')
    app_key = os.getenv('LEANCLOUD_APP_KEY')

    if app_id is None or app_key is None:
        print('Storage can\'t initialize, '
              'please setup environment variable LEANCLOUD_APP_ID and LEANCLOUD_APP_KEY', file=sys.stderr)
    else:
        leancloud.init(app_id, app_key)
