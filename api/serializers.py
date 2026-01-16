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

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'