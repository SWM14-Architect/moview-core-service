#!/bin/bash

echo ">>> pip이 설치되어 있는지 확인합니다."
if ! command -v pip3 &> /dev/null
then
    echo "pip could not be found"
    echo "Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
else
    echo "pip is installed"
fi

echo ">>> python3.8-venv 패키지가 설치되어 있는지 확인합니다."
if ! dpkg -l | grep python3.8-venv
then
    echo "python3.8-venv could not be found"
    echo "Installing python3.8-venv..."
    sudo apt-get update
    sudo apt-get install -y python3.8-venv
else
    echo "python3.8-venv is installed"
fi
