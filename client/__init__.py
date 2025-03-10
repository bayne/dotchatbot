from abc import ABC, abstractmethod
from typing import List, Literal

from parser.transformer import Message
from typing import Literal

ServiceName = Literal[
    "OpenAI",]

class ServiceClient(ABC):
    def __init__(self) -> None: ...
    @abstractmethod
    def create_chat_completion(self, messages: List[Message]) -> Message: ...

def create_client(service_name: ServiceName, api_key: str) -> ServiceClient:
    if service_name == "OpenAI":
        return OpenAI(api_key=api_key)
    else:
        raise ValueError(f"Invalid service name: {service_name}")

from client.openai import OpenAI