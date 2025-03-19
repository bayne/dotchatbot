from typing import Literal

from dotchatbot.client import ServiceClient
from dotchatbot.client.openai import OpenAI

ServiceName = Literal[
    "OpenAI",]


def create_client(
        service_name: ServiceName,
        system_prompt: str,
        api_key: str
) -> ServiceClient:
    if service_name == "OpenAI":
        return OpenAI(api_key=api_key, system_prompt=system_prompt)
    else:
        raise ValueError(f"Invalid service name: {service_name}")
