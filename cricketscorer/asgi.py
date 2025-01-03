"""
ASGI config for cricketscorer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from match import consumers
from django.urls import re_path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cricketscorer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/test/(?P<match_id>\d+)/$',consumers.ScoreUpdateReceiveConsumer.as_asgi())
            ]
        )
    )
})