from typing import Literal, List
from dotchatbot.input.transformer import Message
from abc import ABC, abstractmethod

ServiceName = Literal[
    "OpenAI",]


class ServiceClient(ABC):
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt

    @abstractmethod
    def create_chat_completion(self, messages: List[Message]) -> Message: ...
