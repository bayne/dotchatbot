import re
import zlib
from typing import Callable, List, Iterable
from typing_extensions import Buffer

from client import ServiceClient
from parser.transformer import Message

OutputRenderer = Callable[[List[Message]], str]

def render(messages: List[Message]) -> str:
    if not messages:
        return ""
    result = map(lambda message: f"@@> {message.role}:\n{message.content.strip()}", messages)
    return "\n\n".join(result) + "\n\n"

def _hash_messages(messages: list[Message], length: int = 5) -> str:
    data: Iterable = list(messages)
    data = map(lambda m: m.content, data)
    data: str = "".join(data)
    data: Buffer = bytes(data, "utf-8")
    checksum = zlib.crc32(data) & 0xffffffff
    return format(checksum, 'x').zfill(length)[:length]

def generate_filename(client: ServiceClient, messages: List[Message]) -> str:
    summarize_prompt = Message(role="user", content="Given the conversation so far, summarize it in just 4 words. Only respond with these 4 words")
    content = client.create_chat_completion([*messages, summarize_prompt]).content
    filename = content.strip()
    filename = filename.lower()
    filename = filename.replace(' ', '-')
    filename = re.sub(r"[^A-Za-z0-9\-]", "", filename)
    return f'{filename}-{_hash_messages(messages)}.md'

import output.markdown