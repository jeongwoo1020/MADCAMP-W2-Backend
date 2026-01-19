from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CommunityViewSet, MemberViewSet, PostViewSet, ChatViewSet, AuthViewSet
from api.views import connection_test 

# 1. Router를 통해 API 주소를 자동으로 생성합니다.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'communities', CommunityViewSet)
router.register(r'members', MemberViewSet)
router.register(r'posts', PostViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'auth', AuthViewSet, basename='auth')

# 2. 생성된 주소들을 urlpatterns에 포함시킵니다.
urlpatterns = [
    path('', include(router.urls)),
    path('test/', connection_test),
]