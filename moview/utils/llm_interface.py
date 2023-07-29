import os
import sys
from typing import *

from langchain.callbacks.base import BaseCallbackHandler
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
