# api/services.py
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Count, Q
from rest_framework.exceptions import ValidationError
from .models import User, Community, Member, Post
# JWT 발급을 위한 라이브러리 (설치 필요: djangorestframework-simplejwt)
from rest_framework_simplejwt.tokens import RefreshToken

class AuthService:
    @staticmethod
    def authenticate_google_user(token):
        """
        구글 소셜 로그인 및 유저 생성 서비스
        (실제 구현 시 google-auth 라이브러리를 통한 검증 로직이 추가되어야 함)
        """
        # 1. 구글 토큰 검증 로직 (여기서는 검증되었다고 가정하고 데이터 추출)
        # google_info = verify_google_token(token)
        google_email = "example@gmail.com"
        google_name = "정우"

        # 2. 유저 존재 확인 및 생성
        user, created = User.objects.get_or_create(
            email=google_email,
            defaults={
                'user_name': google_name,
                'score': 0
            }
        )

        # 3. JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return user, tokens

class CommunityService:
    @staticmethod
    def join_community(user, community, nick_name, description=""):
        """프론트에서 받은 닉네임과 소개를 포함하여 가입 처리"""
        if Member.objects.filter(user_id=user, com_id=community).exists():
            raise ValidationError("이미 가입된 커뮤니티입니다.")
        
        return Member.objects.create(
            user_id=user,         # 모델의 FK 필드명
            com_id=community,     # 모델의 FK 필드명
            nick_name=nick_name,
            description=description,
            cert_cnt=0,
            is_late_cnt=0
        )
    @staticmethod
    def get_community_rankings(com_id):
        """커뮤니티 내 유저별 순위 매기기 (인증횟수 DESC, 지각횟수 ASC)"""
        return Member.objects.filter(com_id=com_id)\
            .order_by('-cert_cnt', 'is_late_cnt')

    @staticmethod
    def get_hall_of_shame(com_id):
        """수치의 전당: 인증 요일에만 최신화, 그 외엔 유지"""
        community = Community.objects.get(com_id=com_id)
        now = timezone.now()
        today_date = now.date()
        weekdays_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # 1. 기준이 되는 '대상 날짜(target_date)' 찾기
        target_date = None
        current_check_date = today_date
        
        # 오늘이 인증 요일이고 마감 시간이 지났는지 확인
        is_cert_day = weekdays_map[now.weekday()] in community.cert_days
        is_after_deadline = now.time() > community.cert_time
        
        if is_cert_day and is_after_deadline:
            # Case A: 오늘이 인증 요일이고 시간이 지났으면 오늘이 기준
            target_date = today_date
        else:
            # Case B: 그 외의 경우, 어제부터 과거로 거슬러 올라가며 가장 가까운 인증 요일을 찾음
            for i in range(1, 8):  # 최대 일주일 전까지 탐색
                past_date = today_date - timedelta(days=i)
                if weekdays_map[past_date.weekday()] in community.cert_days:
                    target_date = past_date
                    break
        
        # 2. 만약 커뮤니티가 방금 생성되어 이전 인증일이 아예 없다면 빈 값 반환
        if not target_date:
            return Member.objects.none()
        
        certified_users = Post.objects.filter(
            com_id=com_id, 
            created_at__date=target_date()
        ).values_list('user_id', flat=True)
        
        return Member.objects.filter(com_id=com_id).exclude(user_id__in=certified_users)

class PostService:
    @staticmethod
    def is_user_certified_today(user, community_id):
        """유저가 오늘 해당 커뮤니티에 인증했는지 확인"""
        today = timezone.now().date()
        return Post.objects.filter(
            user=user,
            community_id=community_id,
            created_at__date=today
        ).exists()

    @staticmethod
    @transaction.atomic
    def process_certification(user, com_id, image, latitude, longitude):
        """
        인증하기 핵심 로직: (인증 요일 고려)
        1. 지각 체크 2. 포스트 생성 3. 멤버 카운트++ 4. 유저 점수 업데이트
        """
        community = Community.objects.get(com_id=com_id)
        member = Member.objects.get(user=user, community=community)
        now = timezone.now()
        today_date = now.date()
        
        # 1. 중복 업로드 체크
        already_certified = PostService.is_user_certified_today(user, com_id)
        
        # 2. 요일 및 시간 판정
        weekdays_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        today_str = weekdays_map[now.weekday()]
        is_cert_day = today_str in community.cert_days
        # 지각 여부 계산
        is_late = now.time() > community.cert_time
        
        # 3. 점수 및 카운트 계산
        point = 0
        current_is_late = False
        
        if not already_certified:
            if is_cert_day:
                # [인증 요일] 정시 +10, 지각 +5 (10-5)
                point = 5 if is_late else 10
                current_is_late = is_late
                member.cert_cnt += 1
                if is_late:
                    member.is_late_cnt += 1
            else:
                # [자율 요일] 지각 체크 없이 무조건 +5
                point = 5
                member.cert_cnt += 1
            
            # 유저 점수 및 멤버 통계 반영
            user.score += point
            user.save()
            member.save()
        
        # 4. 포스트 생성
        post = Post.objects.create(
            user_id=user,
            com_id=community,
            image_url=image, # 실제론 S3 업로드 후 URL 저장 로직 필요
            is_late=current_is_late if is_cert_day else False,
            latitude=latitude,
            longitude=longitude
        )
        
        return post

    @staticmethod
    @transaction.atomic
    def rollback_certification(post):
        """포스트 삭제 시 점수 및 카운트 복구"""
        user = post.user
        member = Member.objects.get(user=user, community=post.community)
        
        # 점수 차감 복구
        point = 5 if post.is_late else 10
        user.score -= point
        user.save()
        
        # 멤버 카운트 복구
        member.cert_cnt -= 1
        if post.is_late:
            member.is_late_cnt -= 1
        member.save()
        
        # 포스트 삭제
        post.delete()