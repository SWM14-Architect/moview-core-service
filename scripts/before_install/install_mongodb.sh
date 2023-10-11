#!/bin/bash

if ! command -v mongod &> /dev/null
then
    echo "MongoDB 서버를 찾을 수 없습니다. 설치를 시작합니다..."
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
else
    echo "MongoDB 서버가 이미 설치되어 있습니다."
fi
