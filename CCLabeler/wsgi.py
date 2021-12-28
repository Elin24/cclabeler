"""
WSGI config for CCLabeler project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

from . import utils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CCLabeler.settings')

application = get_wsgi_application()

utils.check_new_images()
