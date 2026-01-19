# api/admin.py
from django.contrib import admin
from .models import User, Community, Member, Post, Chat

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'user_name', 'score', 'created_at', 'updated_at')
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    search_fields = ('user_name', 'username', 'email')

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('com_uuid', 'com_id', 'com_name', 'cert_time', 'created_at')
    readonly_fields = ('com_uuid', 'created_at', 'updated_at')
    search_fields = ('com_name', 'com_id')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('mem_idx', 'user_id', 'com_uuid', 'nick_name', 'cert_cnt', 'is_late_cnt', 'joined_at')
    readonly_fields = ('mem_idx', 'joined_at')
    search_fields = ('nick_name', 'user_id__user_name', 'com_uuid__com_name')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'user_id', 'com_uuid', 'is_late', 'created_at')
    readonly_fields = ('post_id', 'created_at', 'updated_at')
    list_filter = ('is_late', 'created_at')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'post', 'user_id', 'content', 'created_at')
    readonly_fields = ('comment_id', 'created_at', 'updated_at')