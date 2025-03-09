import dataclasses
from getpass import getpass

import keyring
import openai

from client import Client
from parser.transformer import Message

class OpenAI(Client):
    def __init__(self, api_key):
        super().__init__()
        self.client = openai.OpenAI(api_key = api_key)

    def create_chat_completion(self, messages: list[Message]) -> list[Message]:
        request = [
            Message(role="system", content="You are a helpful assistant."),
            *messages,
        ]
        request = map(lambda x: dataclasses.asdict(x), request)
        request = list(request)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=request,
        )
        content = response.choices[0].message.content
        role = response.choices[0].message.role

        messages.append(Message(role=role, content=content))
        return messages