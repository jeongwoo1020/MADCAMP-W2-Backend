# api/serializers.py
from rest_framework import serializers
from .models import User, Community, Member, Post, Chat

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'score', 'interests', 'profile_img_url', 'created_at']
        read_only_fields = ['id', 'created_at']

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    # 유저와 커뮤니티의 상세 정보를 함께 보고 싶다면 아래 주석을 해제하세요
    # user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Member
        fields = '__all__'


class RegisterSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=100, help_text="User's display name")
    profile_img_url = serializers.CharField(help_text="Selected emoji or avatar URL")

class PostSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(use_url=True)
    com_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ['user_id', 'com_uuid', 'com_id', 'image_url', 'latitude', 'longitude', 'is_late']
        # extra_kwargs = {'com_uuid': {'required': False}}

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'