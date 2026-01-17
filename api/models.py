import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Users (커스텀 유저 모델)
class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=100) # 본명
    score = models.FloatField(default=50.0)      # 열정 점수
    interests = models.JSONField(default=list, blank=True) # 관심사
    profile_img_url = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 2. Communities
class Community(models.Model):
    com_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    com_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cert_cnt = models.IntegerField(default=0)
    is_late_cnt = models.IntegerField(default=0)
    report_cnt = models.IntegerField(default=0)
    profile_img_url = models.TextField(null=True, blank=True)
    shame_img_url = models.TextField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

# 4. Posts (인증 포스트)
class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    com_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    image_url = models.TextField()
    is_late = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 5. Chats
class Chat(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    com_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)