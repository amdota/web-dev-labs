"""
ASGI config for webDjangoLabs project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import pollings.routing
from webDjangoLabs.channelsmiddleware import JwtAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webDjangoLabs.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': JwtAuthMiddleware(
        URLRouter(
            pollings.routing.websocket_urlpatterns
        )
    ),
})
