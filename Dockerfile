# 1. 베이스 이미지 선택
# Python 3.11 버전이 설치된 가벼운 리눅스 환경에서 시작합니다.
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
# 컨테이너(가상 컴퓨터) 안에 /app 이라는 폴더를 만들고, 앞으로 모든 작업은 여기서 진행합니다.
WORKDIR /app

# 3. 필요한 파일 복사
# 먼저, 라이브러리 목록 파일만 복사합니다. (Docker 빌드 캐시 효율을 위해)
COPY requirements.txt .

# 4. 라이브러리 설치
# 복사한 requirements.txt를 이용해 컨테이너 안에 모든 라이브러리를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 전체 파일 복사
# 로컬에 있는 모든 파일(main.py, database/, .env 등)을 컨테이너의 /app 폴더 안으로 복사합니다.
COPY . .

# 6. 서버 실행 포트 설정
# 이 컨테이너는 외부와 8000번 포트를 통해 통신할 것임을 알려줍니다.
EXPOSE 8000

# 7. 서버 실행 명령어
# 컨테이너가 시작될 때, 이 명령어를 자동으로 실행하여 FastAPI 서버를 구동합니다.
# --host=0.0.0.0 옵션은 컨테이너 외부에서도 접속할 수 있게 해주는 중요한 설정입니다.
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]