# 1. 파이썬 3.11 버전의 가벼운 리눅스(slim)를 기반으로 합니다.
FROM python:3.11-slim

# 2. 터미널의 출력이 실시간으로 보이게 설정합니다. (디버깅용)
ENV PYTHONUNBUFFERED 1

# 3. 컨테이너 안에서 우리가 작업할 폴더 이름을 /app으로 정합니다.
WORKDIR /app

# 4. (중요!) PostgreSQL 연결에 필요한 리눅스 필수 도구들을 설치합니다.
# 이 단계 덕분에 정우님이 겪으셨던 'psycopg' 설치 에러가 해결됩니다.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. 내 컴퓨터에 있는 requirements.txt를 컨테이너 안으로 복사합니다.
COPY requirements.txt /app/

# 6. 복사한 파일을 보고 필요한 파이썬 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 7. 현재 폴더의 모든 소스 코드를 컨테이너의 /app 폴더로 복사합니다.
COPY . /app/

# 8. 서버를 실행합니다. 0.0.0.0으로 열어야 내 컴퓨터에서 접속이 가능합니다.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]