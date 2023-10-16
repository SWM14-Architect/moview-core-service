#!/bin/bash

source /etc/profile.d/codedeploy.sh

REPOSITORY=/home/ubuntu/app
VENV=$REPOSITORY/venv

echo ">>> 애플리케이션 디렉토리로 이동합니다."
cd $REPOSITORY

echo ">>> Python 가상환경(venv)을 활성화합니다."
source $VENV/bin/activate

echo ">>> log와 pid를 저장할 파일을 생성합니다."
touch app.log

echo ">>> Flask 앱을 실행합니다."
nohup gunicorn app:app --pid gunicorn.pid -b 0.0.0.0:5005 --workers 4 --threads 8 --timeout=120 > app.log 2>&1 &