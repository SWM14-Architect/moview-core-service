#!/bin/bash

REPOSITORY=/home/ubuntu/app

echo ">>> 애플리케이션 디렉토리로 이동합니다."
cd $REPOSITORY

echo ">>> Anaconda 가상환경(moview)을 활성화합니다."
source /home/ubuntu/miniconda/etc/profile.d/conda.sh
conda activate moview

echo ">>> Flask 앱을 실행합니다."
nohup python app.py > app.log 2>&1 &
echo $! > pid.txt