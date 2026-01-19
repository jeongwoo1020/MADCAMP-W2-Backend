# API Documentation

이 문서는 백엔드 API 명세서입니다. 프론트엔드 개발자가 쉽게 이해하고 연동할 수 있도록 작성되었습니다.

## 🔗 Base URL
- 개발 서버: `http://localhost:8000/api/` (예시)
- API Prefix: `/` (urls.py에 따라 root가 api 앱의 urls로 연결됨, 프로젝트 설정 확인 필요)

---

## 🔐 1. 인증 (Authentication)

### 1-1. 구글 로그인
구글 OAuth를 통해 받은 토큰을 백엔드로 전송하여 인증하고, 자체 JWT 토큰(Access/Refresh)을 발급받습니다.

- **URL**: `/google_login/` (AuthViewSet) -> *주의: `urls.py`에 `auth` 관련 라우터 등록 여부 확인 필요. 현재 `views.py`에는 `AuthViewSet`이 정의되어 있으나 `urls.py`에는 등록되어 있지 않습니다. 확인이 필요합니다.*
  - **수정 제안**: `urls.py`에 `router.register(r'auth', AuthViewSet, basename='auth')` 추가 필요.
  - 만약 추가된다면 URL은 `/auth/google_login/`이 됩니다.

- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "token": "GOOGLE_ACCESS_TOKEN_OR_ID_TOKEN"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "user": {
      "user_id": "uuid",
      "user_name": "정우",
      "score": 50.0,
      "interests": [],
      "profile_img_url": "url",
      "created_at": "datetime"
    },
    "tokens": {
      "refresh": "eyJ...",
      "access": "eyJ..."
    }
  }
  ```

---

## 👤 2. 유저 (Users)

### 2-1. 내 프로필 조회
로그인된 사용자의 정보를 조회합니다.

- **URL**: `/users/me/my_profile/` (UserViewSet의 action)
- **Method**: `GET`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Response (200 OK)**:
  ```json
  {
    "user_id": "uuid",
    "user_name": "이름",
    "score": 50.0,
    "interests": ["coding", "reading"],
    "profile_img_url": "url"
  }
  ```

### 2-2. 내 프로필 수정
로그인된 사용자의 정보를 수정합니다.

- **URL**: `/users/me/my_profile/`
- **Method**: `PUT`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Request Body** (수정할 필드만 보냄):
  ```json
  {
    "user_name": "새로운 이름",
    "interests": ["travel"]
  }
  ```
- **Response (200 OK)**: 수정된 유저 정보

---

## 🏘️ 3. 커뮤니티 (Communities)

### 3-1. 커뮤니티 목록 조회
- **URL**: `/communities/`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  [
    {
      "com_id": "uuid",
      "com_name": "알고리즘 스터디",
      "description": "매일 한 문제 풀기",
      "cert_days": ["Mon", "Wed", "Fri"],
      "cert_time": "23:59:00",
      "icon_url": "url"
    },
    ...
  ]
  ```

### 3-2. 커뮤니티 가입
- **URL**: `/communities/{id}/join/`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "nick_name": "코딩왕",
    "description": "열심히 하겠습니다!"
  }
  ```
- **Response (201 Created)**: 생성된 멤버 정보

### 3-3. 커뮤니티 랭킹 조회
- **URL**: `/communities/{id}/rankings/`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  [
    {
      "mem_idx": "uuid",
      "nick_name": "코딩왕",
      "cert_cnt": 10,
      "is_late_cnt": 1
    },
    ...
  ]
  ```

### 3-4. 수치의 전당 (Hall of Shame)
인증 요일에 지각했거나 미인증한 멤버들을 보여줍니다.
- **URL**: `/communities/{id}/hall_of_shame/`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  [
    { "nick_name": "지각생1", ... },
    ...
  ]
  ```

---

## 📸 4. 포스트 (Posts)

### 4-1. 오늘자 포스트 목록 조회
특정 커뮤니티의 오늘 올라온 인증글들을 가져옵니다. 내가 오늘 인증하지 않았다면 다른 사람의 사진은 블러(Masked) 처리되어 보입니다.

- **URL**: `/posts/?com_id={community_uuid}`
- **Method**: `GET`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Query Params**: `com_id` (필수)
- **Response (200 OK)**:
  ```json
  [
    {
      "post_id": "uuid",
      "user_id": "uuid",
      "image_url": "https://... (또는 Masked_Url)",
      "is_late": false,
      "latitude": 37.5,
      "longitude": 127.0,
      "created_at": "..."
    },
    ...
  ]
  ```

### 4-2. 인증하기 (포스트 생성)
사진을 업로드하여 인증합니다. 서버에서 지각 여부 및 점수 계산을 자동으로 수행합니다.

- **URL**: `/posts/`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `com_id`: 커뮤니티 UUID
  - `image_url`: 파일 (이미지) -> *Note: API 필드명은 `image_url`이지만 실제 파일 업로드 시 `request.FILES['image_url']`로 받으므로 키 이름을 맞춰야 함.*
  - `latitude`: 위도 (선택)
  - `longitude`: 경도 (선택)
- **Response (201 Created)**:
  ```json
  {
      "post_id": "...",
      "is_late": false,
      ...
  }
  ```

### 4-3. 포스트 삭제
인증을 취소하고 삭제합니다. 획득했던 점수도 롤백됩니다.
- **URL**: `/posts/{id}/`
- **Method**: `DELETE`
- **Response (204 No Content)**

---

## 🗄️ Database Schema

### User (사용자)
- `user_id` (UUID): PK
- `user_name` (String): 본명 (구글 이름)
- `score` (Float): 열정 점수 (기본 50.0)
- `interests` (JSON): 관심사 목록
- `profile_img_url`: 프로필 이미지

### Community (커뮤니티)
- `com_id` (UUID): PK
- `com_name`: 커뮤니티 이름
- `cert_days` (JSON): 인증 요일 (예: `['Mon', 'Wed']`)
- `cert_time`: 인증 마감 시간 (예: `23:59:00`)

### Member (멤버 - 유저와 커뮤니티의 관계)
- `mem_idx` (UUID): PK
- `user_id`: User FK
- `com_id`: Community FK
- `nick_name`: 커뮤니티 내 닉네임
- `cert_cnt`: 총 인증 횟수
- `is_late_cnt`: 지각 횟수

### Post (인증글)
- `post_id` (UUID): PK
- `user_id`: User FK
- `com_id`: Community FK
- `image_url`: 이미지 주소
- `is_late`: 지각 여부

### Chat (채팅)
- `comment_id`: PK
- `post_id`: Post FK
- `content`: 내용

---

## 🧪 테스트 API
백엔드 연결 확인용
- **URL**: `/test/`
- **Method**: `GET`
- **Response**: `{"message": "백엔드와 연결에 성공했습니다! 🚀"}`
