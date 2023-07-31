import os
import sys
import boto3
from enum import Enum

from moview.utils.singleton_meta_class import SingletonMeta


class EnvironmentEnum(Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEV"
    STAGING = "STA"
    PRODUCTION = "PROD"


class EnvironmentLoader(metaclass=SingletonMeta):
    # 개발자별로 다른 값을 사용해야 하는 파라미터인 경우, 아래 리스트에 파라미터 이름을 추가하면 됩니다.
    USER_SPECIFIC_PARAMETERS = ["openai-api-key"]

    @staticmethod
    def get_aws_iam():
        if sys.platform == 'darwin':  # MacOS
            return os.environ["AWS_IAM"]
        elif sys.platform == 'win32' or sys.platform == 'linux':  # Windows, linux
            return os.getenv("AWS_IAM")

    @staticmethod
    def get_environment():
        if sys.platform == 'darwin':  # MacOS
            return os.environ["MOVIEW_CORE_ENV"]
        elif sys.platform == 'win32' or sys.platform == 'linux':  # Windows, linux
            return os.getenv("MOVIEW_CORE_ENV")

    @staticmethod
    def build_parameter_path(parameter_name):
        environment = EnvironmentLoader.get_environment()
        aws_iam = EnvironmentLoader.get_aws_iam()

        base_path = f"/moview-core/{environment}"

        if parameter_name in EnvironmentLoader.USER_SPECIFIC_PARAMETERS and environment == EnvironmentEnum.DEVELOPMENT.value:  # 개발자별로 다른 값을 사용해야 하고, 개발 환경이라면
            return f"{base_path}/{aws_iam}/{parameter_name}"  # AWS IAM을 path에 추가
        else:
            return f"{base_path}/{parameter_name}"

    @staticmethod
    def get_param(parameter_name):
        ssm = boto3.client('ssm')
        parameter_path = EnvironmentLoader.build_parameter_path(parameter_name)

        response = ssm.get_parameter(Name=parameter_path, WithDecryption=True)
        return response['Parameter']['Value']

    @staticmethod
    def get_open_ai_key():
        if EnvironmentLoader.get_environment() == EnvironmentEnum.LOCAL.value:
            return os.environ.get(EnvironmentLoader.USER_SPECIFIC_PARAMETERS[0])
        elif EnvironmentLoader.get_environment() == EnvironmentEnum.DEVELOPMENT.value:
            return EnvironmentLoader.get_param(EnvironmentLoader.USER_SPECIFIC_PARAMETERS[0])
