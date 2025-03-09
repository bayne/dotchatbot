from abc import ABC, abstractmethod
from typing import List, Literal

from parser.transformer import Message

class ServiceClient(ABC):
    def __init__(self) -> None: ...
    @abstractmethod
    def create_chat_completion(self, messages: List[Message]) -> List[Message]: ...

