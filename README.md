# MADCAMP-W2-Backend - BeReal 프로젝트

이 저장소는 MADCAMP 2주차 BeReal 스타일 앱의 백엔드 서버입니다. Django REST Framework (DRF)를 기반으로 구축되었으며, 유저 인증, 커뮤니티 관리, 일일 인증 및 실시간 채팅 기능을 제공합니다.

## 🛠 기술 스택 (Tech Stack)

-   **프레임워크:** Django 5, Django REST Framework
-   **데이터베이스:** PostgreSQL 16
-   **실시간 통신:** Django Channels, Daphne, Redis
-   **스토리지:** Google Cloud Storage (GCS)
-   **문서화:** drf-spectacular (Swagger/Redoc)
-   **스케줄링:** django-apscheduler (Cron Job)
-   **컨테이너:** Docker, Docker Compose

## 🚀 주요 기능

### 1. 유저 관리 (User Management)
-   JWT 기반 로그인 및 회원가입 
-   프로필 수정 

### 2. 커뮤니티 (Community)
-   커뮤니티 생성 및 가입.
-   **수치의 전당 (Hall of Shame)**: 커뮤니티의 인증 마감 시간(cert_time)과 비교하여 인증에 실패한 멤버들을 갤러리 형식으로 노출.
-   **랭킹 시스템**: 인증 횟수를 기반으로 한 커뮤니티 내 랭킹 제공.

### 3. 포스트 및 인증 (Post & Certification)
-   **일일 인증**: 사진 업로드를 통해 하루를 인증.
-   **지각 처리**: 정해진 시간 이후 인증 시 점수 차감.
-   **GCS 이미지 업로드**: 인증 및 프로필 이미지는 Google Cloud Storage에 저장.
-   **블러 처리 (Blurring)**: 미인증 유저에게는 타인의 사진이 블러 처리되어 미노출, 인증 이후 보이도록 url 설정.

### 4. 실시간 채팅 (Real-time Chat)
-   각 커뮤니티별 WebSocket 기반 채팅방 제공.
-   이전 채팅 내역 불러오는 REST API 제공 (History support).

## 📦 설치 및 실행 가이드

### 필수 요구사항
-   Docker 및 Docker Compose 설치 필요.

### Docker로 실행하기 (권장)

1.  **레포지토리 클론:**
    ```bash
    git clone https://github.com/your-repo/madcamp-w2-backend.git
    cd madcamp-w2-backend
    ```

2.  **환경 설정:**
    -   `config/settings.py` 파일의 설정을 확인하세요.
    -   GCS 연동이 필요한 경우, `config/` 폴더 내에 `gcp-key.json` 등 인증 키 파일을 위치시키세요.

3.  **서비스 시작:**
    ```bash
    docker-compose up --build
    ```
    -   Django (web), PostgreSQL (db), Redis 컨테이너가 실행됩니다.

4.  **API 접속:**
    -   API Root: `http://localhost:8000/api/`
    -   Admin 패널: `http://localhost:8000/admin/`

## 📚 API 문서

`drf-spectacular`를 통해 자동 생성된 API 문서를 확인할 수 있습니다.

-   **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`
-   **Redoc:** `http://localhost:8000/api/schema/redoc/`

## 📂 프로젝트 구조

```
MADCAMP-W2-Backend/
├── api/
│   ├── REST API
│   │   ├── views.py        # API 뷰 (비즈니스 로직)
│   │   ├── urls.py         # REST API 라우팅
│   │   ├── serializers.py  # 데이터 직렬화
│   │   └── models.py       # DB 모델 정의
│   ├── Socket (Real-time)
│   │   ├── consumers.py    # WebSocket 소비자 (핸들러)
│   │   └── routing.py      # WebSocket 라우팅
│   └── Scheduler
│       └── operator.py     # 스케줄러 (지각 체크 등)
├── config/             # 프로젝트 설정 및 URL 라우팅
├── media/              # 미디어 파일 루트
├── Dockerfile          # Django Docker 이미지 빌드 파일
├── docker-compose.yaml # 도커 서비스 오케스트레이션
├── manage.py           # Django 관리 스크립트
└── requirements.txt    # 파이썬 의존성 목록
```
