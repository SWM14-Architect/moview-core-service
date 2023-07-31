import os
import sys
import boto3
from enum import Enum

from moview.utils.singleton_meta_class import SingletonMeta


class EnvironmentEnum(Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"
    STAGING = "sta"
    PRODUCTION = "prod"


class EnvironmentLoader(metaclass=SingletonMeta):
    # 주요 환경 변수명 상수 처리
    MOVIEW_CORE_ENV = "MOVIEW_CORE_ENV"
    AWS_IAM = "AWS_IAM"

    # 개발자별로 다른 값을 사용해야 하는 파라미터인 경우, 아래 리스트에 파라미터 이름을 추가하면 됩니다.
    USER_SPECIFIC_PARAMETERS = ["openai-api-key"]

    @staticmethod
    def get_local_env(local_env_name):
        if sys.platform == 'darwin':  # MacOS
            return os.environ[local_env_name]
        elif sys.platform == 'win32' or sys.platform == 'linux':  # Windows, linux
            return os.getenv(local_env_name)

    @staticmethod
    def build_ssm_parameter_path(parameter_name):
        environment = EnvironmentLoader.get_local_env(EnvironmentLoader.MOVIEW_CORE_ENV)
        aws_iam = EnvironmentLoader.get_local_env(EnvironmentLoader.AWS_IAM)

        base_path = f"/moview-core/{environment}"

        if parameter_name in EnvironmentLoader.USER_SPECIFIC_PARAMETERS and environment == EnvironmentEnum.DEVELOPMENT.value:  # 개발자별로 다른 값을 사용해야 하고, 개발 환경이라면
            return f"{base_path}/{aws_iam}/{parameter_name}"  # AWS IAM을 path에 추가
        else:
            return f"{base_path}/{parameter_name}"

    @staticmethod
    def get_ssm_parameter(parameter_name):
        ssm = boto3.client('ssm')
        parameter_path = EnvironmentLoader.build_ssm_parameter_path(parameter_name)

        response = ssm.get_parameter(Name=parameter_path, WithDecryption=True)
        return response['Parameter']['Value']

    @staticmethod
    def getenv(env_name):
        if EnvironmentLoader.get_local_env(EnvironmentLoader.MOVIEW_CORE_ENV) == EnvironmentEnum.LOCAL.value:
            return EnvironmentLoader.get_local_env(env_name.replace("-", "_").upper())  # local은 시스템 환경 변수를 사용
        else:
            return EnvironmentLoader.get_ssm_parameter(env_name)  # dev, stage, prod는 AWS SSM 파라미터 스토어를 사용
