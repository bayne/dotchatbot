import os
import re
import sys
import zlib
from getpass import getpass
from typing import Optional, List, Any, Iterable

import click
import keyring
from click import UsageError
from click_extra import extra_command
from cloup import option_group, option
from lark import Lark
from rich.console import Console, JustifyMethod
from rich.markdown import Markdown
from typing_extensions import Buffer

from client.client_registry import ServiceName, create_client
from parser import GRAMMAR
from parser.transformer import SectionTransformer, Message

parser = Lark(GRAMMAR, parser='lalr')
transformer = SectionTransformer()

def hash_messages(messages: list[Message], length: int = 5) -> str:
    data: Iterable[Any] = list(messages)
    data = map(lambda m: m.content, data)
    data: str = "".join(data)
    data: Buffer = bytes(data, "utf-8")
    checksum = zlib.crc32(data) & 0xffffffff
    return format(checksum, 'x').zfill(length)[:length]

def parse(document: Optional[str]) -> List[Message]:
    if not document or not document.strip():
        return []
    tree = parser.parse(document)
    return transformer.transform(tree)

def read_messages_from_stdin(messages_from_file: list[Message]) -> List[Message]:
    messages_from_stdin = parse(sys.stdin.read())
    return [*messages_from_file, *messages_from_stdin]

def read_messages_from_file(filename: Optional[str]) -> List[Message]:
    if filename and os.path.exists(filename):
        with open(filename, "r") as f:
            return parse(f.read())
    return []

def read_messages_from_editor(messages_from_file: List[Message], reverse: bool) -> List[Message]:
    if not reverse:
        file_content = click.edit(text=f"{render(messages_from_file)}@@> user:\n\n")
        return parse(file_content)
    else:
        reversed_messages_from_file = reversed(messages_from_file)
        reversed_messages_from_file = list(reversed_messages_from_file)
        file_content = click.edit(text=f"@@> user:\n\n{render(reversed_messages_from_file)}")
        messages: List[Message] = parse(file_content)
        messages = list(reversed(messages))
        return messages

def get_api_key(service_name: ServiceName) -> str:
    api_key = keyring.get_password(service_name.lower(), "api_key")
    if not api_key:
        api_key = getpass(f"Enter your {service_name} API key: ")
        keyring.set_password(service_name.lower(), "api_key", api_key)
    return api_key

def render(messages: List[Message]) -> str:
    if not messages:
        return ""
    result = map(lambda message: f"@@> {message.role}:\n{message.content.strip()}", messages)
    return "\n\n".join(result) + "\n\n"

def rich_print(
        output: str,
        no_pager: bool,
        markdown_justify: JustifyMethod,
        markdown_code_theme: str,
        markdown_hyperlinks: bool,
        markdown_inline_code_lexer: str,
        markdown_inline_code_theme: str,
    ):
    markdown = Markdown(
        output,
        justify=markdown_justify,
        code_theme=markdown_code_theme,
        hyperlinks=markdown_hyperlinks,
        inline_code_lexer=markdown_inline_code_lexer,
        inline_code_theme=markdown_inline_code_theme,
    )
    console = Console()
    if no_pager:
        console.print(markdown)
    else:
        with console.capture() as capture:
            console.print(markdown)
        click.echo_via_pager(capture.get(), color=True)

@extra_command
@click.argument("filename", required=False)
@option_group(
    "Options",
    option("--service-name", "-s", help="The chatbot provider service name", default="OpenAI"),
    option("--re-edit", "-e", is_flag=True, help="Open the response immediately in the editor", default=False),
    option("--no-pager", is_flag=True, help="Do not output using pager", default=False),
    option("--no-rich", is_flag=True, help="Do not output using rich", default=False),
    option("--reverse", "-r", help="Reverse the conversation in the editor", is_flag=True, default=False),
    option("--assume-yes", "-y", help='Automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.', is_flag=True, default=False),
    option("--assume-no", "-n", help='Automatic no to prompts; assume "no" as answer to all prompts and run non-interactively.', is_flag=True, default=False),
)
@option_group(
    "Markdown options",
    option("--markdown-justify", default="default"),
    option("--markdown-code-theme", default="monokai"),
    option("--markdown-hyperlinks"),
    option("--markdown-inline-code-lexer"),
    option("--markdown-inline-code-theme"),
)
def main(
        filename: Optional[str],
        service_name: ServiceName,
        re_edit: bool,
        no_pager: bool,
        no_rich: bool,
        reverse: bool,
        assume_yes: bool,
        assume_no: bool,
        markdown_justify: JustifyMethod,
        markdown_code_theme: str,
        markdown_hyperlinks: bool,
        markdown_inline_code_lexer: str,
        markdown_inline_code_theme: str,
    ) -> None:
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
    client = create_client(service_name=service_name, api_key=api_key)

    messages_from_file = read_messages_from_file(filename)

    if sys.stdin.isatty():
        messages = read_messages_from_editor(messages_from_file, reverse=reverse)
    else:
        messages = read_messages_from_stdin(messages_from_file)

    if not messages or not messages[-1].content.strip() or messages[-1].role != "user":
        raise UsageError("Aborting request due to empty message")

    messages = client.create_chat_completion(messages)
    output = messages[-1].content

    if not re_edit:
        if no_rich or not sys.stdout.isatty():
            print(output)
        else:
            rich_print(output, no_pager, markdown_justify, markdown_code_theme, markdown_hyperlinks,
                       markdown_inline_code_lexer, markdown_inline_code_theme)

    if prompt_user:
        save = click.confirm("Save response?", default=True)
    elif assume_yes:
        save = True
    else:
        save = False

    if not filename and save:
        summarize_prompt = Message(role="user", content="Given the conversation so far, summarize it in just 4 words. Only respond with these 4 words")
        content = client.create_chat_completion([*messages, summarize_prompt])[-1].content
        filename = content.strip()
        filename = filename.lower()
        filename = filename.replace(' ', '-')
        filename = re.sub(r"[^A-Za-z0-9\-]", "", filename)
        filename = f'{filename}-{hash_messages(messages)}.md'

    if filename and save:
        with open(filename, "w") as f:
            f.write(render(messages))
        print(f"Saved to {filename}", file=sys.stderr)


if __name__ == "__main__":
    main(auto_envvar_prefix="DOTCHATBOT")
