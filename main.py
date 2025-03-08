import os
import re
import sys
from getpass import getpass
from typing import Optional

import click
import keyring
from click import UsageError
from lark import Lark, Transformer
from lark.reconstruct import Reconstructor
from openai import OpenAI

GRAMMAR = """
    start: section+
        | content

    section: header content

    header: "@@>" _WS ROLE ":" _WS

    ROLE: /[a-zA-Z]+/

    ?content: (line_without_header)*

    line_without_header: MARKDOWN
        | NL

    MARKDOWN: /(?!@@>).+/

    %import common.WS -> _WS
    %import common.NEWLINE -> NL
    """

parser = Lark(GRAMMAR, parser='lalr')

class SectionTransformer(Transformer):

    def __init__(self):
        super().__init__()

    def start(self, items):
        if items[0].data == "content":
            return [{ "role": "user", "content": "".join(items[0].children)}]

        items = map(lambda item: item.children, items)
        return [{"role": role, "content": "".join(content.children)} for role, content in items]

    def header(self, items):
        return [i.value for i in items if i.type == "ROLE"][0]

    def line_without_header(self, items):
        return items[0].value

transformer = SectionTransformer()

def parse(document: str):
    if not document or not document.strip():
        return None, []
    tree = parser.parse(document)
    return tree, transformer.transform(tree)

def reconstruct(tree, parser):
    return Reconstructor(parser).reconstruct(tree)

def render(messages):
    if not messages:
        return ""
    result = map(lambda message: f"@@> {message['role']}:\n{message['content'].strip()}", messages)
    return "\n\n".join(result) + "\n\n"

@click.command
@click.argument("filename", required=False)
@click.option("--reverse", "-r", help="Reverse the conversation in the editor", is_flag=True, default=False)
@click.option("--assume-yes", "-y", help='Automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.', is_flag=True, default=False)
@click.option("--assume-no", "-n", help='Automatic no to prompts; assume "no" as answer to all prompts and run non-interactively.', is_flag=True, default=False)
def main(filename: Optional[str], reverse: bool, assume_yes: bool, assume_no: bool):
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

    api_key = keyring.get_password("openai", "api_key")
    if not api_key:
        api_key = getpass("Enter your OpenAI API key: ")
        keyring.set_password("openai", "api_key", api_key)

    client = OpenAI(api_key = api_key)

    messages_from_file = []
    if filename and os.path.exists(filename):
        with open(filename, "r") as f:
            tree, messages_from_file = parse(f.read())

    if not sys.stdin.isatty():
        stdin = sys.stdin.read()
        if stdin.startswith("@@>"):
            tree, messages_from_stdin = parse(stdin)
        else:
            messages_from_stdin = [{"role": "user", "content": stdin.strip()}]

        if messages_from_file:
            messages = [*messages_from_file, *messages_from_stdin]
        else:
            messages = messages_from_stdin
    else:
        if not reverse:
            file_content = click.edit(text=f"{render(messages_from_file)}@@> user:\n\n")
            tree, messages = parse(file_content)
        else:
            messages_from_file = reversed(messages_from_file)
            messages_from_file = list(messages_from_file)
            file_content = click.edit(text=f"@@> user:\n\n{render(messages_from_file)}")
            tree, messages = parse(file_content)
            messages = reversed(messages)
            messages = list(messages)

    if not messages or not messages[-1]["content"].strip() or messages[-1]["role"] != "user":
        raise UsageError("Aborting request due to empty message")

    request = [
        {"role": "system", "content": "You are a helpful assistant."},
        *messages,
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=request,
    )
    content = response.choices[0].message.content
    role = response.choices[0].message.role

    messages.append({"role": role, "content": content})

    print(content)

    if prompt_user:
        save = click.confirm("Save response?", default=True)
    elif assume_yes:
        save = True
    else:
        save = False

    if not filename and save:
        request.append({"role": "user", "content": "Given the conversation so far, summarize it in just 4 words. Only respond with these 4 words"})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=request,
        )
        content = response.choices[0].message.content
        filename: str = content.strip()
        filename = filename.lower()
        filename = filename.replace(' ', '-')
        filename = re.sub(r"[^A-Za-z0-9\-]", "", filename)
        filename = f'{filename}.md'

    if filename and save:
        with open(filename, "w") as f:
            f.write(render(messages))
        print(f"Saved to {filename}", file=sys.stderr)


if __name__ == "__main__":
    main()
