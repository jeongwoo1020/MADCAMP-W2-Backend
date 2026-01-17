# api/apps.py
import os
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # 장고는 개발 모드에서 서버를 두 번 띄우기 때문에 (Reloader)
        # 스케줄러가 두 번 실행되지 않도록 환경변수를 체크합니다.
        if os.environ.get('RUN_MAIN'):
            from . import operator
            operator.start()
            print("--- [시스템] APScheduler 스케줄러 가동 중 ---")