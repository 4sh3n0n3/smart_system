import string

from random import choice

import shutil
import signal
import tempfile
import os

from .settings import *

SECRET_KEY = 'fake'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = 'http://testserver/media/'


def signal_handler():
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
