# api/serializers.py
from rest_framework import serializers
from .models import User, Community, Member, Post, Chat

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'login_id', 'user_name', 'score', 'interests', 'profile_img_url', 'created_at']
        read_only_fields = ['user_id', 'created_at']

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
    login_id = serializers.CharField(max_length=50, help_text="User Login ID (unique)")
    password = serializers.CharField(write_only=True, help_text="User Password")
    user_name = serializers.CharField(max_length=100, help_text="User's display name")
    profile_img_url = serializers.CharField(help_text="Selected emoji or avatar URL")

class LoginSerializer(serializers.Serializer):
    login_id = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

class PostSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(use_url=True)
    # com_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'post_id',    
            'user_id', 
            'com_uuid', 
            'image_url', 
            'is_late', 
            'latitude', 
            'longitude', 
            'created_at'  
        ]
        read_only_fields = ['post_id', 'created_at', 'is_late']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'