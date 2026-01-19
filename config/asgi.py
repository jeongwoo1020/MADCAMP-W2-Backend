"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.middleware import JwtAuthMiddleware #user_id 수동 입력이 아닌 JWT 토큰 기반 유저 인증 채팅
import api.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# application = get_asgi_application()

# 1. 장고의 표준 ASGI 애플리케이션 (HTTP 처리)
django_asgi_app = get_asgi_application()

# 2. 프로토콜 라우터 설정
application = ProtocolTypeRouter({
    # http 요청은 기존 장고 방식(Views)으로 처리
    "http": django_asgi_app,
    
    # 웹소켓 요청은 Channels 전용 라우터로 처리
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         api.routing.websocket_urlpatterns # 빈 리스트 대신 실제 패턴 입력
    #     )
    # ),
    "websocket": JwtAuthMiddleware( 
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})