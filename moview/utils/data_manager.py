from typing import *

from langchain.callbacks.base import BaseCallbackHandler
from moview.handlers.custom_callback_handler import CustomCallbackHandler
from langchain.chat_models import ChatOpenAI

import moview.utils.aws_interface as aws

OPENAI_API_KEY_PARAM = "openai-api-key"


class KeyManager:
    def __init__(self):
        self.openai_api_key = aws.getparam(OPENAI_API_KEY_PARAM)


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
            openai_api_key=KeyManager().openai_api_key,
            streaming=streaming,
            callbacks=[callback_handler],
            model_name=model,
            temperature=temperature,
        )

    def get_chat_model(self) -> ChatOpenAI:
        return self.chat
