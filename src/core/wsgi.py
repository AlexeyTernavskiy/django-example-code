# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.core.settings.production")

application = get_wsgi_application()
