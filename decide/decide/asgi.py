import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from store import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decide.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(
            [
                path("ws/votes/", consumers.VoteConsumer.as_asgi()),
            ]
        ),
    }
)
