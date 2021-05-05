"""
WSGI config for youtube project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = StaticFilesHandler( get_wsgi_application())
