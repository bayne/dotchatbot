from abc import ABC, abstractmethod
from typing import List

from dotchatbot.parser import Message


class ServiceClient(ABC):
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt

    @abstractmethod
    def create_chat_completion(self, messages: List[Message]) -> Message: ...
