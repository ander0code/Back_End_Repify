"""
ASGI config for repo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from repo.consumers import TuConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repo.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Aquí puedes añadir WebSocket y otros protocolos
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         path('ws/some_path/', TuConsumer.as_asgi()),
    #     ])
    # ),
})