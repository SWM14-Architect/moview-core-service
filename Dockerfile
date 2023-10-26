# 베이스 이미지
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 추가
COPY . .

# 환경 변수 설정
ENV MOVIEW_CORE_ENV=prod

# 해당 포트를 사용할 것을 선언
EXPOSE 5000

# 애플리케이션 실행
# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5005", "--workers", "4", "--threads", "8", "--timeout=120"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]