# API Documentation

## 🔗 Base URL
- **Base URL**: `http://localhost:8000/api/` (로컬 개발 환경 기준)
- **WebSocket URL**: `ws://localhost:8000/ws/`

---

## 🔐 1. 인증 (Authentication)

### 1-1. 회원가입
아이디, 비밀번호, 닉네임, 프로필 이미지를 입력받아 회원을 생성하고 자동 로그인 처리합니다.

- **URL**: `/auth/register/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "login_id": "testuser123",  // 로그인 시 사용할 id
    "password": "password123!", // 비밀번호
    "user_name": "정우",        // User 본명
    "profile_img_url": "https://example.com/avatar.png" // 이모지 또는 이미지 URL
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "user": {
      "user_id": "uuid-string", // (PK)
      "user_name": "정우",
      "score": 50.0,
      "interests": [],
      "profile_img_url": "...",
      "created_at": "..."
    },
    "user_id": "uuid-string",
    "token": { //JWT token
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
  ```

### 1-2. 로그인
아이디와 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.

- **URL**: `/auth/login/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "login_id": "testuser123",
    "password": "password123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "user": { ... }, // 유저 상세 정보
    "user_id": "uuid-string",
    "token": { //JWT token
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
  ```

---

## 👤 2. 유저 (Users)

### 2-1. 내 프로필 조회
로그인된 사용자의 정보를 조회합니다. (JWT 토큰 기반)

- **URL**: `/users/me/`
- **Method**: `GET`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Response (200 OK)**:
  ```json
  {
    "user_id": "uuid",
    "login_id": "testuser123",
    "user_name": "이름",
    "score": 50.0,
    "interests": ["coding", "reading"], // null일 수 있음
    "profile_img_url": "url",
    "created_at": "datetime"
  }
  ```

### 2-2. 내 프로필 수정
로그인된 사용자의 정보를 수정합니다.

- **URL**: `/users/me/`
- **Method**: `PUT`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Request Body** (수정할 필드만 보냄):
  ```json
  {
    "user_name": "새로운 이름",
    "interests": ["travel"],
    "profile_img_url": "new_url"
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
      "com_id": "알고리즘스터디", // 사용자에게 보여지는 텍스트 ID (검색)
      "com_uuid": "uuid",      // 내부 로직용 고유 UUID (PK)
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
- **URL**: `/communities/join/`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "com_id": "알고리즘스터디", // 커뮤니티의 텍스트 ID (com_id, 검색값)
    "nick_name": "코딩왕",     // 해당 커뮤니티에서 사용할 닉네임
    "description": "열심히 하겠습니다!" // 커뮤니티 가입 시 입력할 프로필 설명
  }
  ```
- **Response (201 Created)**: 생성된 멤버 정보

### 3-3. 커뮤니티 랭킹 조회
- **URL**: `/communities/{com_id}/rankings/` 
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
- **URL**: `/communities/{com_id}/hall_of_shame/`
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

### 4-1. 오늘자 포스트 목록 조회 (수정중)
특정 커뮤니티의 오늘 올라온 인증글들을 가져옵니다. 내가 오늘 인증하지 않았다면 다른 사람의 사진은 블러(Masked) 처리되어 보입니다.

- **URL**: `/posts/?com_id={community_text_id}`
- **Query Params**: `com_id` (커뮤니티의 텍스트 ID, e.g. "알고리즘스터디")
- **Method**: `GET`
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Response (200 OK)**:
  ```json
  [
    {
      "post_id": "uuid",
      "user_id": "uuid",
      "com_id": "알고리즘스터디",
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
  - `com_id`: 커뮤니티 텍스트 ID (String)
  - `image_url`: 파일 객체 (File)
  - `latitude`: 위도 (Double, 선택)
  - `longitude`: 경도 (Double, 선택)
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
- **Header**: `Authorization: Bearer <ACCESS_TOKEN>`
- **Response (204 No Content)**

---

## 💬 5. 실시간 채팅 (WebSockets)
각 커뮤니티별 실시간 채팅을 지원합니다.

- **URL Scheme**: `ws://localhost:8000/ws/chat/{com_uuid}/`
- **Path Parameter**: `{com_uuid}` - 커뮤니티의 고유 UUID (목록 조회 시 `com_uuid` 필드 값 사용)

### 5-1. 메시지 전송 (Client -> Server)
```json
{
  "message": "안녕하세요! 오늘 인증 빡세네요 ㅠㅠ"
}
```

### 5-2. 메시지 수신 (Server -> Client)
다른 유저가 메시지를 보냈을 때 수신되는 데이터입니다.
```json
{
  "message": "안녕하세요! 오늘 인증 빡세네요 ㅠㅠ",
  "nickname": "코딩왕", // 채팅 보낸 사람의 해당 커뮤니티 닉네임
  "user_id": "uuid"    // 보낸 사람의 유저 ID
}
```

### 5-3. 주의사항
- 연결 시 별도의 인증 헤더를 지원하지 않는 경우, 쿼리 파라미터나 쿠키 세션을 활용해야 할 수 있습니다. (현재 구현은 `self.scope['user']`를 참조하므로 세션 인증이 필요할 수 있음)
- 연결 후 메시지 전송은 JSON 문자열로 직렬화하여 보내야 합니다.

---


## 👥 6. 멤버 (Members) 
커뮤니티에 가입된 멤버 정보를 관리하는 API입니다.

### 6-1. 멤버 목록 조회
- **URL**: `/members/get_members//?com_uuid={com_uuid}`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  [
    {
      "mem_idx": "uuid",      // 멤버 고유 ID (PK)
      "nick_name": "uuid",    
      "description": "소개글",
      "cert_cnt": 0,          // 인증 횟수
      "is_late_cnt": 0,       // 지각 횟수
      "report_cnt": 0,        // 신고 횟수
      "profile_img_url": "url",
      "shame_img_url": "url",
      "joined_at": "datetime",
      "user_id": "uuid",      // 유저 ID (FK)
      "com_uuid": "uuid"      // 커뮤니티 ID (FK)
    },
    ...
  ]
  ```

### 6-2. 본인 커뮤니티 조회
로그인 토큰을 기반으로 본인이 속한 커뮤니티를 조회하는 API 입니다.
- **URL**: `/members/my_communities/`
- **Method**: `GET`
- **Response (200 OK)**: =
  ```json
  [
    {
      "com_uuid": "uuid",
      "com_id": "string",
      "com_name": "string",
      "description": "string",
      "cert_days": "string",
      "cert_time": "10:42:24.061000",
      "icon_url": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
  ```

### 6-3. 멤버 정보 수정
- **URL**: `/members/{mem_idx}/`
- **Method**: `PUT` / `PATCH`
- **Request Body**:
  ```json
  {
    "nick_name": "수정할닉네임",
    "description": "수정할소개글"
  }
  ```
- **Response (200 OK)**: 수정된 멤버 객체

### 6-4. 멤버 탈퇴/삭제
- **URL**: `/members/{mem_idx}/`
- **Method**: `DELETE`
- **Response (204 No Content)**

---

## 🧪 테스트 API
백엔드 연결 확인용
- **URL**: `/test/`
- **Method**: `GET`
- **Response**: `{"message": "백엔드와 연결에 성공했습니다! 🚀"}`
