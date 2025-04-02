import re
from typing import Callable
from typing import Iterable
from typing import List

import zlib
from typing_extensions import Buffer

from dotchatbot.client.services import ServiceClient
from dotchatbot.input.transformer import Message

NEW_USER_MESSAGE = "@@> user:\n\n"

OutputRenderer = Callable[[List[Message]], str]


def generate_file_content(messages: List[Message]) -> str:
    if not messages:
        return ""
    result = map(
        lambda message: f"@@> {message.role}:\n{message.content.strip()}",
        messages
    )
    return "\n\n".join(result) + "\n\n"


def _hash_messages(
    messages: list[Message], length: int = 5
) -> str:
    data: Iterable = list(messages)
    data = map(lambda m: m.content, data)
    data: str = "".join(data)
    data: Buffer = bytes(data, "utf-8")
    checksum = zlib.crc32(data) & 0xffffffff
    return format(checksum, 'x').zfill(length)[:length]


def generate_filename(
    client: ServiceClient,
    summary_prompt: str,
    messages: List[Message],
    extension: str
) -> str:
    summarize_prompt = Message(role="user", content=summary_prompt)
    content = client.create_chat_completion(
        [*messages, summarize_prompt]
    ).content
    filename = content.strip()
    filename = filename.lower()
    filename = filename.replace(' ', '-')
    filename = re.sub(r"[^A-Za-z0-9\-]", "", filename)
    return f'{filename}-{_hash_messages(messages)}{extension}'
