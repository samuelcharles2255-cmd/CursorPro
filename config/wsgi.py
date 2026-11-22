"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Run database migrations on startup to ensure all tables exist, and seed jobs & marketplace if empty
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)

    from apps.jobs.models import Job
    if not Job.objects.exists():
        call_command('loaddata', 'jobs_data.json')

    from apps.marketplace.models import Category
    if not Category.objects.exists():
        call_command('seed_marketplace')
except Exception as _e:
    logging.getLogger('django').warning(f"Startup initialization note: {_e}")

app = application
