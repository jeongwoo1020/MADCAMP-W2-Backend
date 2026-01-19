from rest_framework import viewsets, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from .models import User, Community, Member, Post, Chat
from .serializers import *
from .services import PostService, CommunityService, AuthService
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

# 1. 회원가입 및 로그인 (Google Auth)
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={200: UserSerializer},
        summary="간편 회원가입",
        description="이름과 아바타 URL을 받아 유저를 생성합니다."
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_name = serializer.validated_data['user_name']
        profile_img_url = serializer.validated_data['profile_img_url']
        
        # AuthService에서 회원가입 처리
        user = AuthService.register_user(user_name, profile_img_url)

        # JWT 토큰 발급
        token = RefreshToken.for_user(user)
        refresh = str(token)
        access = str(token.access_token)
        
        return Response({
            'user': UserSerializer(user).data,
            'user_id': user.user_id,
            'token': {
                'access': access,
                'refresh': refresh,
            }
        }, status=status.HTTP_201_CREATED)


# 2. 유저 정보 관리
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get', 'put'], url_path='me')
    def my_profile(self, request):
        user = request.user
        if request.method == 'GET':
            # 내 점수, 가입 커뮤니티 목록, 관심사 등 반환
            return Response(UserSerializer(user).data)
        elif request.method == 'PUT':
            # 프로필 수정
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

# 3. 커뮤니티 관리
class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    
    # 커뮤니티 ID 검색 (기본 제공) 및 가입 로직
    @action(detail=False, methods=['post']) # detail=True에서 False로 변경 (pk 없이 호출 가능)
    def join(self, request):
        com_id_text = request.data.get('com_id') # 사용자가 입력한 문자열 ID
        try:
            community = Community.objects.get(com_id=com_id_text)
        except Community.DoesNotExist:
             return Response({"error": "존재하지 않는 커뮤니티 ID입니다."}, status=404)

        nick_name = request.data.get('nick_name')
        description = request.data.get('description', "")
        
        if not nick_name:
            return Response({"error": "닉네임은 필수입니다."}, status=400)
        
        # Member 레코드 생성 및 가입 로직은 Service에서 처리
        member = CommunityService.join_community(
            user=request.user, 
            community=community,
            nick_name=nick_name,
            description=description
        )
        return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)
    
    # 커뮤니티 내 랭킹 조회
    @action(detail=True, methods=['get'])
    def rankings(self, request, pk=None):
        rankings = CommunityService.get_community_rankings(pk)
        return Response(rankings)

    # 수치의 전당 조회
    @action(detail=True, methods=['get'])
    def hall_of_shame(self, request, pk=None):
        shame_list = CommunityService.get_hall_of_shame(pk)
        return Response(shame_list)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

# 4. 포스트 관리
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="오늘자 포스트 목록 조회",
        description="커뮤니티 ID(com_id)를 받아 오늘 작성된 게시글을 불러옵니다. 미인증 시 타인의 사진은 블러 처리됩니다.",
        parameters=[
            OpenApiParameter(
                name='com_id', 
                type=OpenApiTypes.INT, 
                location=OpenApiParameter.QUERY, 
                description="커뮤니티 고유 ID",
                required=True
            ),
        ]
    )
    # 오늘자 포스트 불러오기 + 블러 처리
    def list(self, request):
        com_id_text = request.query_params.get('com_id')
        try:
            community = Community.objects.get(com_id=com_id_text)
        except Community.DoesNotExist:
             return Response({"error": "존재하지 않는 커뮤니티 ID입니다."}, status=404)
        
        com_uuid = community.com_uuid # 실제 DB 조회용 UUID
        today = timezone.now().date()
        
        # 1. 오늘 나의 인증 여부 확인 (Service 호출)
        has_certified = PostService.is_user_certified_today(request.user, com_uuid)
        
        # 2. 오늘자 포스트 쿼리
        posts = Post.objects.filter(com_uuid=com_uuid, created_at__date=today)
        serializer = self.get_serializer(posts, many=True)
        data = serializer.data
        
        # 3. 미인증 시 타인의 이미지를 마스킹(Blur) 처리
        if not has_certified:
            MASKED_URL = "Masked_Url" # "https://your-s3-bucket.com/static/blurred-placeholder.png"
            for p in data:
                # '내 글'이 아닌 경우에만 마스킹 처리
                # Serializer outputs 'user_id' (UUID) for the ForeignKey
                if str(p['user_id']) != str(request.user.user_id):
                    p['image_url'] = MASKED_URL
                    
        return Response(data)

    # 인증하기 (사진 업로드)
    @extend_schema(
        summary="인증 사진 업로드 (GCS)",
        description="이미지 파일(image_url)을 직접 업로드하여 GCS에 저장합니다.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'com_id': {'type': 'string', 'description': '커뮤니티 ID (문자열)'},
                    'image_url': {'type': 'string', 'format': 'binary', 'description': '인증 사진 파일'},
                    'latitude': {'type': 'number', 'format': 'double'},
                    'longitude': {'type': 'number', 'format': 'double'},
                },
                'required': ['com_id', 'image_url']
            }
        },
        responses={201: PostSerializer}
    )
    def create(self, request):
        # 사진 업로드, 지각 체크, 점수 가중치 계산은 모두 Service에서 수행
        # 문자열 com_id로 uuid 조회
        try:
           community = Community.objects.get(com_id=request.data.get('com_id'))
        except Community.DoesNotExist:
           return Response({"error": "Invalid community ID"}, status=400)

        post = PostService.process_certification(
            user=request.user,
            com_id=community, # Service가 instance를 받도록 수정 혹은 uuid 전달
            image=request.FILES.get('image_url'),
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

    # 포스트 삭제 (점수/카운트 복구 포함)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 삭제 시 수반되는 점수 복구 로직은 Service에서 처리
        PostService.rollback_certification(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

#테스트용
@api_view(['GET'])
def connection_test(request):
    return Response({"message": "백엔드와 연결에 성공했습니다! 🚀"})