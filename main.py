import dataclasses
import os
import re
import sys
import zlib
from getpass import getpass
from typing import Optional, List, Any

import click
import keyring
from click import UsageError
from lark import Lark, Tree, Token
from lark.reconstruct import Reconstructor

from client.openai import OpenAI
from parser import GRAMMAR
from parser.transformer import SectionTransformer, Message

parser = Lark(GRAMMAR, parser='lalr')
transformer = SectionTransformer()

def hash_messages(messages: list[Message], length=5):
    data = list(messages)
    data = map(lambda m: m.content, data)
    data = "".join(data)
    data = bytes(data, "utf-8")
    checksum = zlib.crc32(data) & 0xffffffff
    return format(checksum, 'x').zfill(length)[:length]

def parse(document: str) -> tuple[Tree[Token] | None, Any]:
    if not document or not document.strip():
        return None, []
    tree = parser.parse(document)
    return tree, transformer.transform(tree)

def read_messages_from_stdin(messages_from_file: list[Message]) -> tuple[Tree[Token], List[Message]]:
    tree, messages_from_stdin = parse(sys.stdin.read())
    messages = [*messages_from_file, *messages_from_stdin]
    return tree, messages

def read_messages_from_file(filename: Optional[str]) -> tuple[Tree[Token], List[Message]]:
    if filename and os.path.exists(filename):
        with open(filename, "r") as f:
            return parse(f.read())
    return Tree("", []), []

def read_messages_from_editor(messages_from_file: list[Message], reverse: bool) -> tuple[Tree[Token], List[Message]]:
    if not reverse:
        file_content = click.edit(text=f"{render(messages_from_file)}@@> user:\n\n")
        return parse(file_content)
    else:
        messages_from_file = reversed(messages_from_file)
        messages_from_file = list(messages_from_file)
        file_content = click.edit(text=f"@@> user:\n\n{render(messages_from_file)}")
        tree, messages = parse(file_content)
        messages = list(reversed(messages))
        return tree, messages

def reconstruct(tree, parser):
    return Reconstructor(parser).reconstruct(tree)

def get_api_key(service_name: str) -> str:
    api_key = keyring.get_password(service_name.lower(), "api_key")
    if not api_key:
        api_key = getpass(f"Enter your {service_name} API key: ")
        keyring.set_password(service_name.lower(), "api_key", api_key)
    return api_key

def create_chat_completion(client, messages: list[Message]) -> list[Message]:
    request = [
        Message(role="system", content="You are a helpful assistant."),
        *messages,
    ]
    request = map(lambda x: dataclasses.asdict(x), request)
    request = list(request)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=request,
    )
    content = response.choices[0].message.content
    role = response.choices[0].message.role

    messages.append(Message(role=role, content=content))
    return messages

def render(messages) -> str:
    if not messages:
        return ""
    result = map(lambda message: f"@@> {message.role}:\n{message.content.strip()}", messages)
    return "\n\n".join(result) + "\n\n"

@click.command
@click.argument("filename", required=False)
@click.option("--service-name", "-s", help="The chatbot provider service name", default="OpenAI")
@click.option("--reverse", "-r", help="Reverse the conversation in the editor", is_flag=True, default=False)
@click.option("--assume-yes", "-y", help='Automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.', is_flag=True, default=False)
@click.option("--assume-no", "-n", help='Automatic no to prompts; assume "no" as answer to all prompts and run non-interactively.', is_flag=True, default=False)
def main(filename: Optional[str], service_name: str, reverse: bool, assume_yes: bool, assume_no: bool):
    """
    Starts a session with the chatbot, resume by providing FILENAME
    """
    if assume_yes and assume_no:
        raise UsageError("--assume-yes and --assume-no are mutually exclusive")

    prompt_user = not assume_no and not assume_yes

    if sys.stdin.isatty() and not sys.stdout.isatty():
        raise UsageError("STDOUT must not be TTY when STDIN is TTY")

    if not sys.stdin.isatty() and prompt_user:
        raise UsageError("Must use -y or -n when STDIN is not TTY")

    api_key = get_api_key(service_name)

    client = OpenAI(api_key = api_key)

    tree_from_file, messages_from_file = read_messages_from_file(filename)

    if sys.stdin.isatty():
        tree, messages = read_messages_from_editor(messages_from_file, reverse=reverse)
    else:
        tree, messages = read_messages_from_stdin(messages_from_file)

    if not messages or not messages[-1].content.strip() or messages[-1].role != "user":
        raise UsageError("Aborting request due to empty message")

    messages = client.create_chat_completion(messages)

    print(messages[-1].content)

    if prompt_user:
        save = click.confirm("Save response?", default=True)
    elif assume_yes:
        save = True
    else:
        save = False

    if not filename and save:
        summarize_prompt = Message(role="user", content="Given the conversation so far, summarize it in just 4 words. Only respond with these 4 words")
        content = client.create_chat_completion([*messages, summarize_prompt])[-1].content
        filename: str = content.strip()
        filename = filename.lower()
        filename = filename.replace(' ', '-')
        filename = re.sub(r"[^A-Za-z0-9\-]", "", filename)
        filename = f'{filename}-{hash_messages(messages)}.md'

    if filename and save:
        with open(filename, "w") as f:
            f.write(render(messages))
        print(f"Saved to {filename}", file=sys.stderr)


if __name__ == "__main__":
    main()
