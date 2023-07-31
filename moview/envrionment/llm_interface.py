import os

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.chat_models import ChatOpenAI

from moview.utils.singleton_meta_class import SingletonMeta
import moview.envrionment.aws_interface as aws
from moview.envrionment.environment_loader import EnvironmentLoader, EnvironmentEnum

OPENAI_API_KEY_PARAM = "openai-api-key"


class LLMApiKeyLoader(metaclass=SingletonMeta):
    def __init__(self):
        if EnvironmentLoader.get_environment() == EnvironmentEnum.TEST.value:
            self.openai_api_key = os.environ.get(OPENAI_API_KEY_PARAM)
        elif EnvironmentLoader.get_environment() == EnvironmentEnum.DEVELOPMENT.value:
            self.openai_api_key = aws.getparam(OPENAI_API_KEY_PARAM)


# 아래 코드는 팩토리 메서드 패턴이나 추상 팩토리 패턴이 적용된 것이 아닙니다.
# Simple Factory 패턴인데, 엄밀히 말하면 디자인 패턴은 아닙니다.
class LLMModelFactory:
    """
    정적 메서드는 self를 받지 않으므로 인스턴스 속성에는 접근할 수 없습니다. 그래서 보통 정적 메서드는 인스턴스 속성, 인스턴스 메서드가 필요 없을 때 사용합니다.
    정적 메서드는 m순수 함수(pure function)를 만들 때 사용합니다. 순수 함수는 부수 효과(side effect)가 없고 입력 값이 같으면 언제나 같은 출력 값을 반환합니다. 즉, 정적 메서드는 인스턴스의 상태를 변화시키지 않는 메서드를 만들 때 사용합니다.
    """

    @staticmethod
    def create_chat_open_ai(temperature: float) -> ChatOpenAI:
        return ChatOpenAI(openai_api_key=LLMApiKeyLoader().openai_api_key,
                          temperature=temperature, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                          callbacks=[StreamingStdOutCallbackHandler()])
