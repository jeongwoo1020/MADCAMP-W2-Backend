from rest_framework import authentication
from rest_framework import exceptions
from .models import User
import uuid

class UserIdAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 1. 헤더에서 X-User-ID 가져오기
        user_id = request.META.get('HTTP_X_USER_ID')
        
        if not user_id:
            return None # 인증 실패가 아니라, 다른 인증 방식 시도하도록 넘김

        try:
            # 2. 유저 조회
            user = User.objects.get(user_id=user_id)
        except (User.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
