from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets
from .models import User, Community, Member, Post, Chat
from .serializers import *
from .services import PostService, CommunityService, AuthService
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import api_view

# 1. 회원가입 및 로그인 (Google Auth)
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={200: UserSerializer},
        summary="회원가입",
        description="ID/PW/이름/아바타를 받아 유저를 생성합니다."
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_name = serializer.validated_data['user_name']
        profile_img_url = serializer.validated_data['profile_img_url']
        login_id = serializer.validated_data['login_id']
        password = serializer.validated_data['password']
        
        # AuthService에서 회원가입 처리
        user = AuthService.register_user(user_name, profile_img_url, login_id, password)

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

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer}, # 실제로는 토큰과 유저 정보
        summary="로그인",
        description="ID/PW로 로그인하여 JWT 토큰을 발급받습니다."
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        login_id = serializer.validated_data['login_id']
        password = serializer.validated_data['password']
        
        user = AuthService.login_user(login_id, password)
        
        if user is None:
            return Response({"error": "ID 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
            
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
        }, status=status.HTTP_200_OK)


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # 커뮤니티 ID 검색 (기본 제공) 및 가입 로직
    @extend_schema(
        summary="커뮤니티 가입",
        description="닉네임과 함께 프로필, 수치의 전당에 박제될 이미지를 직접 업로드합니다.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'com_id': {'type': 'string'},
                    'nick_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'profile_image': {'type': 'string', 'format': 'binary'},
                    'shame_image': {'type': 'string', 'format': 'binary'} # 파일 형식 지정
                },
                'required': ['com_id', 'nick_name', 'profile_image', 'shame_image']
            }
        },
        responses={201: MemberSerializer}
    )
    @action(detail=False, methods=['post'])
    def join(self, request):
        com_id_text = request.data.get('com_id') # 사용자가 입력한 문자열 ID
        try:
            community = Community.objects.get(com_id=com_id_text)
        except Community.DoesNotExist:
             return Response({"error": "존재하지 않는 커뮤니티 ID입니다."}, status=404)

        nick_name = request.data.get('nick_name')
        description = request.data.get('description', "")
        profile_image = request.FILES.get('profile_image')
        shame_image = request.FILES.get('shame_image')
        
        if not nick_name:
            return Response({"error": "닉네임은 필수입니다."}, status=400)
        
        # Member 레코드 생성 및 가입 로직은 Service에서 처리
        member = CommunityService.join_community(
            user=request.user, 
            community=community,
            nick_name=nick_name,
            description=description,
            profile_img_url=profile_image,
            shame_img_url=shame_image
        )
        return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)
    
    # 커뮤니티 내 랭킹 조회
    @action(detail=True, methods=['get'])
    def rankings(self, request, pk=None):
        rankings = CommunityService.get_community_rankings(pk)
        serializer = MemberSerializer(rankings, many=True)
        return Response(serializer.data)

    # 수치의 전당 조회
    @action(detail=True, methods=['get'])
    def hall_of_shame(self, request, pk=None):
        shame_list = CommunityService.get_hall_of_shame(pk)
        serializer = MemberSerializer(shame_list, many=True, context={'request': request})
        return Response(serializer.data)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    
    # URL: GET /api/members/my_communities/
    # token 기반 유저가 속한 communities 반환 
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_communities(self, request):
        user = request.user
        
        memberships = Member.objects.filter(user_id=user).select_related('com_uuid')
        communities = [m.com_uuid for m in memberships]
        
        serializer = CommunitySerializer(communities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # URL: GET /api/members/get_members/?com_uuid=...
    @extend_schema(
        summary="커뮤니티 멤버 목록 조회",
        description="com_uuid를 사용하여 해당 커뮤니티의 멤버 리스트를 가져옵니다.",
        parameters=[OpenApiParameter(name='com_uuid', description='커뮤니티의 고유 UUID (PK)', required=False, type=str)],
        responses={200: MemberSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def get_members(self, request):
        com_uuid = request.query_params.get('com_uuid')
        # com_id = request.query_params.get('com_id') # 텍스트 ID

        if com_uuid:
            try:
                members = Member.objects.filter(com_uuid=com_uuid)
            except Community.DoesNotExist:
                return Response({"error": "해당 커뮤니티를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "com_uuid가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MemberSerializer(members, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 4. 포스트 관리
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    # 1. 오늘자 포스트 불러오기 + 블러 처리
    @extend_schema(
        summary="오늘자 포스트 목록 조회 (UUID 기반)",
        description="커뮤니티의 고유 UUID를 받아 오늘 작성된 게시글을 불러옵니다. 미인증 시 타인의 사진은 블러 처리됩니다.",
        parameters=[
            OpenApiParameter(
                name='com_uuid', 
                type=str, 
                location=OpenApiParameter.QUERY, 
                description="커뮤니티 고유 UUID (PK)",
                required=True
            ),
        ]
    )
    def list(self, request):
        com_uuid = request.query_params.get('com_uuid')
        if not com_uuid:
            return Response({"error": "com_uuid 파라미터가 필요합니다."}, status=400)
        
        today = timezone.now().date()
        
        # 1. 오늘 나의 인증 여부 확인 (Service 호출)
        has_certified = PostService.is_user_certified_today(request.user, com_uuid)
        
        # 2. 오늘자 포스트 쿼리
        posts = Post.objects.filter(com_uuid=com_uuid, created_at__date=today)
        serializer = self.get_serializer(posts, many=True)
        data = serializer.data
        
        # 3. 미인증 시 타인의 이미지를 마스킹(Blur) 처리
        if not has_certified:
            MASKED_URL = "https://storage.googleapis.com/madcamp-w2-storage/blur.jpg" # "https://your-s3-bucket.com/static/blurred-placeholder.png"
            for p in data:
                # '내 글'이 아닌 경우에만 마스킹 처리
                # Serializer outputs 'user_id' (UUID) for the ForeignKey
                if str(p['user_id']) != str(request.user.user_id):
                    p['image_url'] = MASKED_URL
                    
        return Response(data)

    # 2. 인증하기 (사진 업로드)
    @extend_schema(
        summary="인증 사진 업로드 (GCS)",
        description="커뮤니티 고유 UUID(com_uuid)와 이미지 파일을 전송하여 인증을 완료합니다.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'com_uuid': { 
                        'type': 'string', 
                        'format': 'uuid', 
                        'description': '커뮤니티 고유 UUID (PK)'
                    },
                    'image_url': {'type': 'string', 'format': 'binary', 'description': '인증 사진 파일'},
                    'latitude': {'type': 'number', 'format': 'double'},
                    'longitude': {'type': 'number', 'format': 'double'},
                },
                'required': ['com_uuid', 'image_url']
            }
        },
        responses={201: PostSerializer}
    )
    def create(self, request):
        # 사진 업로드, 지각 체크, 점수 가중치 계산은 모두 Service에서 수행
        # 문자열 com_id로 uuid 조회
        com_uuid = request.data.get('com_uuid')
        try:
            # PK인 com_uuid로 즉시 조회하여 효율성을 높입니다.
            community = Community.objects.get(com_uuid=com_uuid)
        except Community.DoesNotExist:
            return Response({"error": "존재하지 않는 커뮤니티 UUID입니다."}, status=status.HTTP_400_BAD_REQUEST)

        post = PostService.process_certification(
            user=request.user,
            com_id=community, 
            image=request.FILES.get('image_url'),
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

    # 3. 나의 포스트 불러오기 (캘린더)
    def get_serializer_class(self):
        if self.action == 'my_history':
            return PostHistorySerializer
        return PostSerializer
    
    @extend_schema(
        summary="내 전체 포스트 히스토리 조회",
        description="내가 모든 커뮤니티에 올린 글을 가져오며, 커뮤니티 이름(com_name)이 포함됩니다.",
        responses={200: PostHistorySerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-history')
    def my_history(self, request):
        posts = Post.objects.filter(user_id=request.user)\
                    .select_related('com_uuid')\
                    .order_by('-created_at')
        serializer = self.get_serializer(posts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
    # 4. 포스트 삭제 (점수/카운트 복구 포함)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 삭제 시 수반되는 점수 복구 로직은 Service에서 처리
        PostService.rollback_certification(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 5. 채팅 관리
class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    
    @extend_schema(
        summary="채팅 내역 조회",
        description="특정 커뮤니티의 이전 대화 내역을 불러옵니다.",
        parameters=[
            OpenApiParameter(name='com_uuid', type=str, location='query', required=True)
        ]
    )
    @action(detail=False, methods=['get'], url_path='chat_history')
    def chat_history(self, request):
        com_uuid = request.query_params.get('com_uuid')
        
        if not com_uuid:
            return Response({"error": "com_uuid가 필요합니다."}, status=400)

        # 해당 커뮤니티의 메시지를 최신순(또는 과거순)으로 정렬하여 가져옵니다.
        messages = Chat.objects.filter(com_uuid=com_uuid).order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    

# 테스트 API
@api_view(['GET'])
def connection_test(request):
    return Response({"message": "백엔드와 연결에 성공했습니다! 🚀"})