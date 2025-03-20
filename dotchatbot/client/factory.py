from typing import Literal

from dotchatbot.client.services import ServiceClient
from dotchatbot.client.openai import OpenAI
from dotchatbot.client.openai import ChatModel

ServiceName = Literal[
    "OpenAI",]


def create_client(
    service_name: ServiceName,
    system_prompt: str,
    api_key: str,
    openai_model: ChatModel,
) -> ServiceClient:
    if service_name == "OpenAI":
        return OpenAI(
            api_key=api_key,
            system_prompt=system_prompt,
            model=openai_model
        )
    else:
        raise ValueError(f"Invalid service name: {service_name}")
