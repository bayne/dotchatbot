from typing import Iterable
from typing import List

from google.genai import Client
from google.genai.types import GenerateContentConfig

from dotchatbot.client.services import ServiceClient
from dotchatbot.input.transformer import Message


def _message_param(
    message: Message
) -> str:
    return message.content


class Google(ServiceClient):
    def __init__(
        self,
        system_prompt: str,
        api_key: str,
        model: str
    ):
        super().__init__(system_prompt=system_prompt)
        self.model = model
        self.client = Client(api_key=api_key)
        self.config = GenerateContentConfig(
            system_instruction=system_prompt
        )

    def create_chat_completion(self, messages: list[Message]) -> Message:
        messages: Iterable[str] = map(_message_param, messages)
        messages: List[str] = list(messages)
        response = self.client.models.generate_content(
            model=self.model,
            config=self.config,
            contents=messages,
        )
        content = response.text

        if not content:
            raise ValueError("Empty response")

        return Message(role="assistant", content=content)
