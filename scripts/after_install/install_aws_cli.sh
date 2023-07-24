#!/bin/bash

echo ">>> AWS CLI가 설치되어 있는지 확인합니다."
if ! command -v aws &> /dev/null
then
    echo "AWS CLI를 찾을 수 없습니다."
    echo "AWS CLI를 설치합니다..."
    sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    sudo unzip awscliv2.zip
    sudo ./aws/install
else
    echo "AWS CLI가 이미 설치되어 있습니다."
fi
