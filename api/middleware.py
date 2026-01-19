import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 1. URL 쿼리 스트링에서 토큰 추출 (예: ws://...?token=TOKEN_VALUE)
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = dict(qp.split("=") for qp in query_string.split("&") if "=" in qp)
        token = query_params.get("token")

        if token:
            try:
                # 2. JWT 토큰 디코딩
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                # SimpleJWT는 보통 user_id를 'user_id' 혹은 'id' 키에 담습니다.
                user_id = payload.get("user_id")
                
                # 3. scope['user']에 유저 정보 저장
                scope["user"] = await get_user(user_id)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, Exception):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)