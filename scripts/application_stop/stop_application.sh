#!/bin/bash

REPOSITORY=/home/ubuntu/app

echo ">>> 애플리케이션 디렉토리로 이동합니다."
cd $REPOSITORY

echo ">>> Flask 앱이 실행중인지 확인합니다."
GUNICORN_PID=$(ps aux | grep 'gunicorn' | grep 'app:app' | awk '{print $2}')

if [ ! -z "$GUNICORN_PID" ]; then
    echo ">>> 작동중인 Flask 앱을 중지합니다."
    kill -15 $GUNICORN_PID
    sleep 5  # 프로세스가 종료되기 위한 대기 시간

    if ps -p $GUNICORN_PID > /dev/null; then
       echo ">>> Gunicorn 프로세스가 아직 종료되지 않았습니다. 강제 종료합니다."
       kill -9 $GUNICORN_PID
    fi
else
    echo ">>> 현재 실행 중인 Flask 앱이 없습니다. 앱 중지를 스킵합니다."
fi

echo ">>> 기존에 배포된 애플리케이션 파일 제거를 시도합니다."
if [ -d "$REPOSITORY" ]; then
    echo ">>> 애플리케이션 디렉토리가 존재합니다. 삭제를 시작합니다."
    sudo rm -rf $REPOSITORY
else
    echo ">>> 애플리케이션 디렉토리가 존재하지 않습니다. 디렉토리 삭제를 스킵합니다."
fi