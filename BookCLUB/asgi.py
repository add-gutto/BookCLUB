import os
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BookCLUB.settings")


application = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP normal
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
