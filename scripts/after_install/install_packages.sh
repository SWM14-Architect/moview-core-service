#!/bin/bash

REPOSITORY=/home/ubuntu/app
VENV=$REPOSITORY/venv

echo ">>> 애플리케이션 디렉토리로 이동합니다."
cd $REPOSITORY

echo ">>> Python 가상환경(venv)을 생성하고, 활성화합니다."
python3 -m venv $VENV
source $VENV/bin/activate

echo ">>> requirements.txt에 기록된 패키지를 설치합니다."
pip install -r requirements.txt
