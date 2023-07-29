#!/bin/bash

echo ">>> MOVIEW_CORE_ENV 환경 변수 설정을 확인합니다."

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

source /home/ubuntu/.bashrc
echo ">>> MOVIEW_CORE_ENV 환경 변수 설정이 적용되었습니다."
