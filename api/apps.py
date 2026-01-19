# api/apps.py
import os
import sys
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # 1. 'runserver' 명령어일 때만 실행하도록 방어 (migrate 등의 환경에서 에러 방지)
        # 0.0.0.0:8000 등 다양한 실행 옵션이 있을 수 있으므로 'runserver' 포함 여부 확인
        if 'runserver' not in sys.argv:
            return

        # 2. 장고 리로더(Reloader)로 인해 서버가 두 번 실행되는 것 방지
        if os.environ.get('RUN_MAIN'):
            from . import operator
            try:
                operator.start()
                print("--- [시스템] APScheduler 스케줄러 가동 중 ---")
            except Exception as e:
                # DB 테이블이 아직 생성되지 않은 경우(초기화 시점) 에러가 날 수 있음
                print(f"--- [주의] 스케줄러 시작 실패 (DB 상태 확인 필요): {e} ---")