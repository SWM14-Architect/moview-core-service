#!/bin/bash

echo ">>> pip이 설치되어 있는지 확인합니다."
if ! command -v pip3 &> /dev/null
then
    echo "pip을 찾을 수 없습니다."
    echo "pip 설치 중..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
else
    echo "pip이 이미 설치되어 있습니다."
fi

echo ">>> python3.8-venv 패키지가 설치되어 있는지 확인합니다."
if ! dpkg -l | grep python3.8-venv
then
    echo "python3.8-venv 패키지를 찾을 수 없습니다."
    echo "python3.8-venv 설치 중..."
    sudo apt-get update
    sudo apt-get install -y python3.8-venv
else
    echo "python3.8-venv 패키지가 이미 설치되어 있습니다."
fi
