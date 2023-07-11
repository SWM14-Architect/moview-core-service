#!/bin/bash

REPOSITORY=/home/ubuntu/app

echo ">>> 애플리케이션 디렉토리로 이동합니다."
cd $REPOSITORY

echo ">>> Flask 앱이 실행중인지 확인합니다."
if [ -f pid.txt ]; then
    echo ">>> 작동중인 Flask 앱을 중지합니다."
    kill $(cat pid.txt)
    rm pid.txt
else
    echo ">>> 현재 실행 중인 Flask 앱이 없습니다."
fi
