"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import logging
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

logger = logging.getLogger('django')

# Initialize Django apps registry first
django_asgi_app = get_asgi_application()

# Run database migrations and seeding on startup now that apps registry is fully ready
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
    logger.warning(f"Startup initialization note: {_e}")


async def application(scope, receive, send):
    """
    ASGI middleware that normalizes response headers to lowercase bytes.
    ASGI 3.0 requires header names to be lowercased bytes (e.g. b"set-cookie"),
    preventing edge reverse proxies (like Wasmer Edge) from crashing on title-cased headers.
    """
    if scope['type'] == 'http':
        response_started = False

        async def send_wrapper(message):
            nonlocal response_started
            if message['type'] == 'http.response.start':
                response_started = True
                raw_headers = message.get('headers', [])
                normalized_headers = [
                    (
                        name.lower() if isinstance(name, bytes) else str(name).lower().encode('ascii'),
                        value
                    )
                    for name, value in raw_headers
                ]
                message = {**message, 'headers': normalized_headers}
            await send(message)

        try:
            await django_asgi_app(scope, receive, send_wrapper)
        except Exception as exc:
            logger.error(f"ASGI unhandled error for {scope.get('path')}: {exc}", exc_info=True)
            if not response_started:
                error_body = f"Internal Server Error: {exc}".encode("utf-8")
                await send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [
                        (b"content-type", b"text/plain; charset=utf-8"),
                        (b"content-length", str(len(error_body)).encode("ascii")),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": error_body,
                    "more_body": False,
                })
    else:
        await django_asgi_app(scope, receive, send)


app = application
