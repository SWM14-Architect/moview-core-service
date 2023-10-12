import os
import sys
import boto3
from enum import Enum

from moview.utils.singleton_meta_class import SingletonMeta


class EnvironmentEnum(Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class EnvironmentLoader(metaclass=SingletonMeta):
    # 주요 환경 변수명 상수 처리
    MOVIEW_CORE_ENV = "MOVIEW_CORE_ENV"
    MOVIEW_IS_LOCAL = "MOVIEW_IS_LOCAL"
    AWS_IAM = "AWS_IAM"

    # 개발자별로 다른 값을 사용해야 하는 파라미터인 경우, 아래 리스트에 파라미터 이름을 추가하면 됩니다.
    USER_SPECIFIC_PARAMETERS = ["openai-api-key", "google-cloud-api-key", "kakao-client-id"]

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

        # 개발자별로 다른 값을 사용해야 하고, 로컬 환경이라면 AWS IAM을 path에 추가
        if parameter_name in EnvironmentLoader.USER_SPECIFIC_PARAMETERS and environment == EnvironmentEnum.LOCAL.value:
            return f"{base_path}/{aws_iam}/{parameter_name}"  # AWS IAM을 path에 추가
        else:
            return f"{base_path}/{parameter_name}"

    @staticmethod
    def get_ssm_parameter(parameter_name):
        ssm = boto3.client('ssm', region_name='ap-northeast-2')
        parameter_path = EnvironmentLoader.build_ssm_parameter_path(parameter_name)

        try:
            response = ssm.get_parameter(Name=parameter_path, WithDecryption=True)
        except Exception as e:
            raise Exception(f"\n{parameter_path} 환경 변수를 가져오는 중 에러가 발생했습니다.\nERROR:\n{e}")

        return response['Parameter']['Value']



    @staticmethod
    def getenv(env_name):
        is_local = EnvironmentLoader.get_local_env(EnvironmentLoader.MOVIEW_IS_LOCAL)
        if is_local is not None and is_local.upper() == "TRUE":
            # MOVIEW_IS_LOCAL이 True인 경우 시스템 환경 변수를 사용
            env_value = EnvironmentLoader.get_local_env(env_name.replace("-", "_").upper())
            if env_value is None:
                raise Exception(f"{env_name} 환경 변수가 Local에서 설정되지 않았습니다.")
            return env_value
        else:
            # local, dev, prod는 AWS SSM 파라미터 스토어를 사용
            return EnvironmentLoader.get_ssm_parameter(env_name)
