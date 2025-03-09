from typing import Literal

from client.openai import OpenAI
from client.service_client import ServiceClient

ServiceName = Literal[
    "OpenAI",]

def create_client(service_name: ServiceName, api_key: str) -> ServiceClient:
    if service_name == "OpenAI":
        return OpenAI(api_key=api_key)
    else:
        raise ValueError(f"Invalid service name: {service_name}")