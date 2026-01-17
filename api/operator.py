# api/operator.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Community, Post, Member, User

# 실행할 함수를 함수 밖으로 독립시킵니다. (Serialization 에러 방지)
def auto_penalty():
    """자정 점수 차감 핵심 로직"""
    now = timezone.now()
    yesterday = now.date() - timedelta(days=1)
    
    weekdays_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    today_weekday = yesterday.weekday()
    yesterday_str = weekdays_map[today_weekday]

    print(f"--- [스케줄러] {yesterday} 미인증자 페널티 부여 시작 ---")

    try:
        with transaction.atomic():
            # 1. 어제가 인증 요일이었던 커뮤니티들 조회
            communities = Community.objects.filter(cert_days__contains=yesterday_str)
            total_penalized = 0

            for com in communities:
                # 2. 어제 인증 포스트를 올린 유저 ID들
                certified_ids = Post.objects.filter(
                    com_id=com,
                    created_at__date=yesterday
                ).values_list('user_id', flat=True)

                # 3. 미인증 멤버들 조회 및 점수 차감 (-10점)
                shame_members = Member.objects.filter(com_id=com).exclude(user_id__in=certified_ids)

                for member in shame_members:
                    user = member.user_id
                    user.score -= 10.0
                    user.save()
                    total_penalized += 1

            print(f"--- [스케줄러] 총 {total_penalized}명 차감 완료 ---")
    except Exception as e:
        print(f"--- [스케줄러 에러] {e} ---")

def start():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # 함수 이름(auto_penalty)만 적어줍니다.
    scheduler.add_job(
        auto_penalty,
        trigger='cron',
        hour=0,
        minute=1,
        id='midnight_penalty',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()