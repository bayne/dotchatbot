# from typing import List, Literal
#
# from client.openai import OpenAI
# from parser.transformer import Message
#
# ServiceName = Literal[
#     "OpenAI",]
#
# class ServiceClient:
#     def __init__(self) -> None: ...
#     def create_chat_completion(self, messages: List[Message]) -> List[Message]: ...
#
# def create_client(service_name: ServiceName, **kwargs: dict) -> ServiceClient:
#     return {
#         "OpenAI": OpenAI,
#     }[service_name](**kwargs)