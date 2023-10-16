#!/bin/bash

echo ">>> MOVIEW_CORE_ENV 환경 변수 설정을 확인합니다."

# /etc/profile.d/codedeploy.sh
ENV_FILE="/etc/profile.d/codedeploy.sh"

if [[ ! -f $ENV_FILE ]]; then
    sudo touch $ENV_FILE
    echo ">>> $ENV_FILE 파일을 생성하였습니다."
fi

if grep -q 'export MOVIEW_CORE_ENV=' $ENV_FILE; then
    if ! grep -q 'export MOVIEW_CORE_ENV="prod"' $ENV_FILE; then
        sudo sed -i '/export MOVIEW_CORE_ENV=/d' $ENV_FILE
        echo 'export MOVIEW_CORE_ENV="prod"' | sudo tee -a $ENV_FILE > /dev/null
        echo ">>> MOVIEW_CORE_ENV 환경 변수가 잘못 설정되어 있었습니다. 'prod'로 재설정하였습니다."
    else
        echo ">>> MOVIEW_CORE_ENV 환경 변수가 이미 올바르게 설정되어 있습니다."
    fi
else
    echo 'export MOVIEW_CORE_ENV="prod"' | sudo tee -a $ENV_FILE > /dev/null
    echo ">>> MOVIEW_CORE_ENV 환경 변수가 설정되지 않았습니다. 'prod'로 설정하였습니다."
fi

# .bashrc
if grep -q 'export MOVIEW_CORE_ENV=' /home/ubuntu/.bashrc; then
    if ! grep -q 'export MOVIEW_CORE_ENV="prod"' /home/ubuntu/.bashrc; then
        sed -i '/export MOVIEW_CORE_ENV=/d' /home/ubuntu/.bashrc
        echo 'export MOVIEW_CORE_ENV="prod"' >> /home/ubuntu/.bashrc
        echo ">>> MOVIEW_CORE_ENV 환경 변수가 잘못 설정되어 있었습니다. 'prod'로 재설정하였습니다."
    else
        echo ">>> MOVIEW_CORE_ENV 환경 변수가 이미 올바르게 설정되어 있습니다."
    fi
else
    echo 'export MOVIEW_CORE_ENV="prod"' >> /home/ubuntu/.bashrc
    echo ">>> MOVIEW_CORE_ENV 환경 변수가 설정되지 않았습니다. 'prod'로 설정하였습니다."
fi

echo ">>> AWS_DEFAULT_REGION 환경 변수 설정을 확인합니다."

if ! grep -q 'export AWS_DEFAULT_REGION=' /home/ubuntu/.bashrc; then
    echo 'export AWS_DEFAULT_REGION="ap-northeast-2"' >> /home/ubuntu/.bashrc
    echo ">>> AWS_DEFAULT_REGION 환경 변수가 설정되지 않았습니다. 'ap-northeast-2'로 설정하였습니다."
else
    echo ">>> AWS_DEFAULT_REGION 환경 변수가 이미 설정되어 있습니다."
fi

source /home/ubuntu/.bashrc
echo ">>> MOVIEW_CORE_ENV 환경 변수 설정이 적용되었습니다."