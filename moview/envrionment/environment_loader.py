import os
import sys
from enum import Enum


class EnvironmentEnum(Enum):
    TEST = "test"
    DEVELOPMENT = "DEV"
    STAGING = "STA"
    PRODUCTION = "PROD"


class EnvironmentLoader:

    @staticmethod
    def get_environment():
        if sys.platform == 'darwin':  # MacOS
            return os.environ["MOVIEW_CORE_ENV"]
        elif sys.platform == 'win32' or sys.platform == 'linux':  # Windows, linux
            return os.getenv("MOVIEW_CORE_ENV")
