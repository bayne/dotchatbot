from typing import Iterable

import openai
from openai.types import ChatModel
from openai.types.chat import ChatCompletionAssistantMessageParam
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionUserMessageParam

from dotchatbot.client.services import ServiceClient
from dotchatbot.input.transformer import Message

SupportedChatCompletionType = (
    ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
    ChatCompletionAssistantMessageParam)


def _chat_completion_message_param(
    message: Message
) -> SupportedChatCompletionType:
    if message.role == "system":
        return ChatCompletionSystemMessageParam(
            content=message.content, role="system"
        )
    elif message.role == "user":
        return ChatCompletionUserMessageParam(
            content=message.content, role="user"
        )
    elif message.role == "assistant":
        return ChatCompletionAssistantMessageParam(
            content=message.content, role="assistant"
        )
    else:
        raise ValueError(f"Invalid role: {message.role}")


class OpenAI(ServiceClient):
    def __init__(
        self, system_prompt: str, api_key: str, model: ChatModel
    ):
        super().__init__(system_prompt=system_prompt)
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def create_chat_completion(self, messages: list[Message]) -> Message:
        request: Iterable[Message] = [
            Message(role="system", content=self.system_prompt), *messages, ]
        request: Iterable[ChatCompletionMessageParam] = map(
            _chat_completion_message_param, request
        )
        request: Iterable[ChatCompletionMessageParam] = list(request)
        response = self.client.chat.completions.create(
            model=self.model, messages=request
        )
        content = response.choices[0].message.content
        role = response.choices[0].message.role

        if not content:
            raise ValueError("Empty response")

        return Message(role=role, content=content)
