from typing import Literal

from anthropic.types import ModelParam
from openai.types import ChatModel

from dotchatbot.client.anthropic import Anthropic
from dotchatbot.client.google import Google
from dotchatbot.client.openai import OpenAI
from dotchatbot.client.services import ServiceClient

ServiceName = Literal["OpenAI", "Anthropic", "Google",]


def create_client(
    service_name: ServiceName,
    system_prompt: str,
    api_key: str,
    openai_model: ChatModel,
    anthropic_model: ModelParam,
    anthropic_max_tokens: int,
    google_model: str,
) -> ServiceClient:
    if service_name == "OpenAI":
        return OpenAI(
            api_key=api_key, system_prompt=system_prompt, model=openai_model
        )
    elif service_name == "Anthropic":
        return Anthropic(
            api_key=api_key,
            system_prompt=system_prompt,
            model=anthropic_model,
            max_tokens=anthropic_max_tokens
        )
    elif service_name == "Google":
        return Google(
            api_key=api_key,
            system_prompt=system_prompt,
            model=google_model,
        )
    else:
        raise ValueError(f"Invalid service name: {service_name}")
