import os
import sys
from typing import *

from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from moview.handlers.custom_callback_handler import CustomCallbackHandler
from langchain.chat_models import ChatOpenAI

from moview.utils.singleton_meta_class import SingletonMeta


class LLMApiKeyLoader(metaclass=SingletonMeta):
    def __init__(self):
        self.openai_api_key = None
        if sys.platform == 'darwin':
            # MacOS
            self.openai_api_key = os.environ["OPENAI_API_KEY"]
        elif sys.platform == 'win32' or sys.platform == 'linux':
            # Windows, Linux
            self.openai_api_key = os.getenv("OPENAI_API_KEY")


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


class ChatManager:
    def __init__(
            self,
            callback_handler: Type[BaseCallbackHandler] = CustomCallbackHandler(),
            streaming: bool = True,
            model: str = "gpt-3.5-turbo",
            temperature: float = 0.5
    ):
        """
        Args:
            callback_handler: CallbackHandler
            streaming: Streaming
            model: GPT Model
            temperature: Temperature
        """
        self.chat = ChatOpenAI(
            openai_api_key=LLMApiKeyLoader().openai_api_key,
            streaming=streaming,
            callbacks=[callback_handler],
            model_name=model,
            temperature=temperature,
        )

    def get_chat_model(self) -> ChatOpenAI:
        return self.chat
