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
    MOVIEW_NO_SSM = "MOVIEW_NO_SSM"
    AWS_IAM = "AWS_IAM"

    # 개발자별로 다른 값을 사용해야 하는 파라미터인 경우, 아래 리스트에 파라미터 이름을 추가하면 됩니다.
    USER_SPECIFIC_PARAMETERS = ["openai-api-key", "google-cloud-api-key", "kakao-client-id"]

    @staticmethod
    def get_local_env(local_env_name):
        '''
        로컬 환경의 환경 변수를 반환합니다.
        '''

        if sys.platform == 'darwin':  # MacOS
            return os.environ[local_env_name]
        elif sys.platform == 'win32' or sys.platform == 'linux':  # Windows, linux
            return os.getenv(local_env_name)

    @staticmethod
    def build_ssm_parameter_path(parameter_name):
        '''
        AWS SSM 파라미터 스토어의 path를 결정하기 위한 함수로, parameter_name에 해당하는 path를 반환합니다.

        현재 개발 환경이 LOCAL이며, parameter_name이 USER_SPECIFIC_PARAMETER에 해당 되는 값일 경우에는 개발자별로 다른 값을 사용해야 합니다.
        이런 경우에는 AWS IAM을 path에 추가하여, 개발자별로 다른 값을 사용할 수 있도록 합니다.
        '''
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
        '''
        AWS SSM 파라미터 스토어에서 parameter_name에 해당하는 환경 변수를 반환합니다.
        '''

        ssm = boto3.client('ssm', region_name='ap-northeast-2')
        parameter_path = EnvironmentLoader.build_ssm_parameter_path(parameter_name)

        try:
            response = ssm.get_parameter(Name=parameter_path, WithDecryption=True)
        except Exception as e:
            raise Exception(f"\n{parameter_path} 환경 변수를 가져오는 중 에러가 발생했습니다.\nERROR:\n{e}")

        return response['Parameter']['Value']

    @staticmethod
    def getenv(env_name):
        '''
        env_name에 해당하는 환경 변수를 반환합니다.

        SSM을 사용하지 않는 경우, 로컬 환경의 환경 변수를 반환합니다.
        그 외에는 AWS SSM을 이용하여 환경 변수를 반환합니다.
        '''

        use_aws_ssm = EnvironmentLoader.get_local_env(EnvironmentLoader.MOVIEW_NO_SSM)
        if use_aws_ssm is not None and use_aws_ssm.upper() == "TRUE":
            # MOVIEW_IS_LOCAL이 True인 경우 시스템 환경 변수를 사용
            env_value = EnvironmentLoader.get_local_env(env_name.replace("-", "_").upper())
            if env_value is None:
                raise Exception(f"{env_name} 환경 변수가 Local에서 설정되지 않았습니다.")
            return env_value
        else:
            # local, dev, prod는 AWS SSM 파라미터 스토어를 사용
            return EnvironmentLoader.get_ssm_parameter(env_name)

    @staticmethod
    def is_prod_env():
        '''
        현재 환경이 prod인지 판단합니다.
        '''
        return EnvironmentLoader.get_local_env(EnvironmentLoader.MOVIEW_CORE_ENV) == EnvironmentEnum.PRODUCTION.value

