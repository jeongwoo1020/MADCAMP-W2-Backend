# api/admin.py
from django.contrib import admin
from .models import User, Community, Member, Post, Chat

admin.site.register(User)
admin.site.register(Community)
admin.site.register(Member)
admin.site.register(Post)
admin.site.register(Chat)