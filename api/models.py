import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# admin 계정 생성 용 
class UserManager(BaseUserManager):
    def create_user(self, login_id, user_name, password=None, **extra_fields):
        if not login_id:
            raise ValueError('아이디(login_id)는 필수입니다.')
        
        user = self.model(
            login_id=login_id,
            user_name=user_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login_id=None, user_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # 만약 장고가 login_id 자리에 값을 안 넣고 username으로 보냈을 경우를 대비합니다.
        if login_id is None:
            login_id = extra_fields.get('username')

        return self.create_user(
            login_id=login_id, 
            user_name=user_name, 
            password=password, 
            **extra_fields
        )

# 1. Users (커스텀 유저 모델)
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login_id = models.CharField(max_length=50, unique=True, null=True) # 로그인 ID
    user_name = models.CharField(max_length=100) # 본명
    score = models.FloatField(default=50.0)      # 열정 점수
    interests = models.JSONField(default=list, blank=True) # 관심사
    profile_img_url = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False) # 관리자 사이트 접속 권한
    is_active = models.BooleanField(default=True)  # 계정 활성화 여부 (기본 True)
    
    objects = UserManager() # 이 매니저를 연결해줘야 합니다.

    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['user_name']
    
    def __str__(self):
        return self.user_name

# 2. Communities
class Community(models.Model):
    com_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    com_id = models.CharField(max_length=50, unique=True, help_text="User defined ID") # 사용자가 입력하는 ID
    com_name = models.CharField(max_length=200)
    description = models.TextField()
    # cert_type = models.CharField(max_length=50) 
    cert_days = models.JSONField(default=list) # 선택 요일 ['Mon', 'Wed']
    cert_time = models.TimeField()              # 인증 마감 시간
    icon_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 3. Members (User <-> Community 연결 및 추가 정보)
class Member(models.Model):
    mem_idx = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    com_uuid = models.ForeignKey(Community, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cert_cnt = models.IntegerField(default=0)
    is_late_cnt = models.IntegerField(default=0)
    report_cnt = models.IntegerField(default=0)
    # profile_img_url = models.TextField(null=True, blank=True)
    profile_img_url = models.ImageField(upload_to='profile/', null=True, blank=True)
    # shame_img_url = models.TextField(null=True, blank=True)
    shame_img_url = models.ImageField(upload_to='shame/', null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    # def __str__(self):
    #     # 닉네임이 있으면 닉네임을, 없으면 유저 ID를 반환하도록 방어 코드 작성
    #     return f"{self.nick_name or self.user.user_name} ({self.com_uuid})"
    def __str__(self):
        try:
            # 1. 닉네임 확인 (필드명이 nick_name인지 nickname인지 확인 필요)
            name = getattr(self, 'nick_name', None) or getattr(self, 'nickname', None)
            
            # 2. 유저 이름 확인 (user_id라는 FK를 통해 User 객체에 접근)
            if not name and self.user_id:
                name = self.user_id.user_name
                
            # 3. 커뮤니티 ID 확인
            com = "No Community"
            if self.com_uuid:
                com = self.com_uuid.com_id

            # 최종 문자열 조합 (이 값들이 None이면 "Unknown"으로 대체)
            return f"{name or 'Unknown'} ({com})"
            
        except Exception:
            # 혹시 위 로직에서도 에러가 나면 그냥 PK(UUID)라도 반환
            return str(self.pk)

import os

def rename_image_path(instance, filename):
    # 파일 확장자 추출 (예: .jpg, .png)
    ext = filename.split('.')[-1]
    # post_id를 파일명으로 사용 (예: 550e8400-e29b-41d4-a716-446655440000.jpg)
    filename = f"{instance.post_id}.{ext}"
    # 'posts/UUID.jpg' 경로 반환
    return os.path.join('posts/', filename)

# 4. Posts (인증 포스트)
class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    com_uuid = models.ForeignKey(Community, on_delete=models.CASCADE)
    # image_url = models.TextField()
    # image_url = models.ImageField(upload_to='posts/', null=True, blank=True)
    image_url = models.ImageField(upload_to=rename_image_path, null=True, blank=True)
    is_late = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 5. Chats
class Chat(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    com_uuid = models.ForeignKey(Community, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # 채팅은 보통 시간순으로 가져오므로 정렬 설정을 추가하면 편합니다.
        ordering = ['created_at']