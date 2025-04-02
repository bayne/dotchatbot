from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Literal

from dotchatbot.input.transformer import Message

ServiceName = Literal["OpenAI",]


class ServiceClient(ABC):
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt

    @abstractmethod
    def create_chat_completion(self, messages: List[Message]) -> Message: ...
