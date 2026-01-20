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
    community_details = CommunitySerializer(source='com_uuid', read_only=True)
    
    class Meta:
        model = Member
        fields = ['mem_idx', 'user_id', 'com_uuid', 'community_details', 'nick_name', 'description', 'cert_cnt', 'is_late_cnt', 'shame_img_url', 'profile_img_url', 'joined_at']
        read_only_fields = ['mem_idx', 'joined_at']


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
        
class PostHistorySerializer(serializers.ModelSerializer):
    com_name = serializers.ReadOnlyField(source='com_uuid.com_name')

    class Meta:
        model = Post
        fields = [
            'post_id',    
            'user_id', 
            'com_uuid',
            'com_name',
            'image_url', 
            'is_late', 
            'created_at'  
        ]

class ChatSerializer(serializers.ModelSerializer):
    sender_nickname = serializers.SerializerMethodField()
    sender_id = serializers.ReadOnlyField(source='user_id.user_id')

    class Meta:
        model = Chat
        fields = ['user_id', 'sender_id', 'sender_nickname', 'content', 'created_at']
        
    def get_sender_nickname(self, obj):
        # 현재 채팅 메시지의 '유저'와 '커뮤니티' 정보를 동시에 만족하는 '멤버'를 찾습니다.
        try:
            member = Member.objects.get(user_id=obj.user_id, com_uuid=obj.com_uuid)
            return member.nick_name
        except Member.DoesNotExist:
            return obj.user_id.user_name