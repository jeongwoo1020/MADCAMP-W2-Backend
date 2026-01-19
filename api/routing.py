# api/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws/chat/<uuid>/ 형식의 요청을 ChatConsumer로 연결
    re_path(r'ws/chat/(?P<com_uuid>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]