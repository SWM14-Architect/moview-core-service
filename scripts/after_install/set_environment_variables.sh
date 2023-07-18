#!/bin/bash

# AWS CLI를 사용하여 Parameter Store에서 값을 검색
echo ">>> AWS Systems Manager Parameter Store로부터 환경변수를 불러옵니다."
CORE_DEV_DB_HOST=$(aws ssm get-parameter --name "/moview-core/dev/db-host" --with-decryption --query "Parameter.Value" --output text)
CORE_DEV_DB_PORT=$(aws ssm get-parameter --name "/moview-core/dev/db-port" --with-decryption --query "Parameter.Value" --output text)
CORE_DEV_DB_USERNAME=$(aws ssm get-parameter --name "/moview-core/dev/db-username" --with-decryption --query "Parameter.Value" --output text)
CORE_DEV_DB_PASSWORD=$(aws ssm get-parameter --name "/moview-core/dev/db-password" --with-decryption --query "Parameter.Value" --output text)

# 환경변수 설정
export CORE_DEV_DB_HOST=$CORE_DEV_DB_HOST
export CORE_DEV_DB_PORT=$CORE_DEV_DB_PORT
export CORE_DEV_DB_USERNAME=$CORE_DEV_DB_USERNAME
export CORE_DEV_DB_PASSWORD=$CORE_DEV_DB_PASSWORD