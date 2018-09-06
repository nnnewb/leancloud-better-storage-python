import os
import sys

app_id = os.getenv('LEANCLOUD_APP_ID')
app_key = os.getenv('LEANCLOUD_APP_KEY')

if app_id is None or app_key is None:
    print('Storage can\'t initialize leancloud sdk, '
          'please set LEANCLOUD_APP_ID and LEANCLOUD_APP_KEY environment variables then try again. '
          'Test abort.',
          file=sys.stderr)
    sys.exit(1)
