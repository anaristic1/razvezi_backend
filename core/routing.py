from django.urls import re_path
from .consumers import RouteConsumer

websocket_urlpatterns = [
    re_path(r"ws/routes/$", RouteConsumer.as_asgi()),
]
