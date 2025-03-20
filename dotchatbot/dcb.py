import os
import sys
from getpass import getpass
from typing import get_args
from typing import Optional

import click
import keyring
from click import UsageError
from click_extra import extra_command
from cloup import option
from cloup import option_group
from openai.types import ChatModel
from rich.console import JustifyMethod

from dotchatbot.client.factory import create_client
from dotchatbot.client.factory import ServiceName
from dotchatbot.output.file import generate_file_content
from dotchatbot.output.file import generate_filename
from dotchatbot.output.markdown import Renderer
from dotchatbot.input.parser import Parser

APP_NAME = "dotchatbot"
os.makedirs(click.get_app_dir(APP_NAME), exist_ok=True)

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful assistant."""

DEFAULT_SUMMARY_PROMPT = """\
Given the conversation so far, summarize it in just 4 words. \
Only respond with these 4 words"""

DEFAULT_SESSION_HISTORY_FILE = os.path.join(
    click.get_app_dir(APP_NAME),
    ".dotchatbot-history"
)
DEFAULT_SESSION_FILE_LOCATION = os.path.join(
    click.get_app_dir(APP_NAME),
    "sessions"
)
os.makedirs(DEFAULT_SESSION_FILE_LOCATION, exist_ok=True)
DEFAULT_SESSION_FILE_EXT = ".dcb"


def get_api_key(service_name: ServiceName) -> str:
    api_key = keyring.get_password(service_name.lower(), "api_key")
    if not api_key:
        api_key = getpass(f"Enter your {service_name} API key: ")
        keyring.set_password(service_name.lower(), "api_key", api_key)
    return api_key


@extra_command
@click.argument("filename", required=False)
@option_group(
    "Options",
    option(
        "--system-prompt", "-p",
        help="The default system prompt to use",
        default=DEFAULT_SYSTEM_PROMPT
    ),
    option(
        "--no-pager",
        is_flag=True,
        help="Do not output using pager",
        default=False
    ),
    option(
        "--no-rich",
        is_flag=True,
        help="Do not output using rich",
        default=False
    ),
    option(
        "--reverse",
        "-r",
        help="Reverse the conversation in the editor",
        is_flag=True,
        default=False
    ),
    option(
        "--assume-yes",
        "-y",
        help='''\
Automatic yes to prompts; \
assume "yes" as answer to all prompts and run non-interactively.\
''',
        is_flag=True,
        default=False
    ),
    option(
        "--assume-no",
        "-n",
        help='''\
Automatic no to prompts; \
assume "no" as answer to all prompts and run non-interactively.\
''',
        is_flag=True,
        default=False
    ),
    option(
        "--current-directory",
        "-c",
        help="Use the current directory as the session file location",
        is_flag=True,
        default=False
    ),
    option(
        "--session-history-file",
        help="The file where the session history is stored",
        default=DEFAULT_SESSION_HISTORY_FILE
    ),
    option(
        "--session-file-location",
        help="The location where session files are stored",
        default=DEFAULT_SESSION_FILE_LOCATION
    ),
    option(
        "--session-file-ext",
        help="The extension to use for session files",
        default=DEFAULT_SESSION_FILE_EXT
    ),
    option(
        "--summary-prompt",
        help="""\
The prompt to use for the summary (for building the filename for the session)\
""",
        default=DEFAULT_SUMMARY_PROMPT
    ),
    option(
        "--service-name", "-s",
        help="The chatbot provider service name",
        default="OpenAI"
    ),
)
@option_group(
    "OpenAI options",
    option(
        "--openai-model",
        default="gpt-4o",
        type=click.Choice(get_args(ChatModel)),
    )
)
@option_group(
    "Markdown options",
    option(
        "--markdown-justify",
        default="default",
        type=click.Choice(get_args(JustifyMethod)),
    ),
    option("--markdown-code-theme", default="monokai"),
    option("--markdown-hyperlinks", is_flag=True, default=False),
    option("--markdown-inline-code-lexer"),
    option("--markdown-inline-code-theme"),
)
def main(
    filename: Optional[str],
    system_prompt: str,
    no_pager: bool,
    no_rich: bool,
    reverse: bool,
    assume_yes: bool,
    assume_no: bool,
    current_directory: bool,
    session_history_file: str,
    session_file_location: str,
    session_file_ext: str,
    summary_prompt: str,
    service_name: ServiceName,
    openai_model: ChatModel,
    markdown_justify: JustifyMethod,
    markdown_code_theme: str,
    markdown_hyperlinks: bool,
    markdown_inline_code_lexer: str,
    markdown_inline_code_theme: str,
) -> None:
    """
    Starts a session with the chatbot, resume by providing FILENAME.
    Provide - for FILENAME to use the previous session
    (stored in LAST_SESSION_FILE).
    """
    if assume_yes and assume_no:
        raise UsageError("--assume-yes and --assume-no are mutually exclusive")

    prompt_user = not assume_no and not assume_yes

    if sys.stdin.isatty() and not sys.stdout.isatty():
        raise UsageError("STDOUT must not be TTY when STDIN is TTY")

    if not sys.stdin.isatty() and prompt_user:
        raise UsageError("Must use -y or -n when STDIN is not TTY")

    api_key = get_api_key(service_name)
    client = create_client(
        service_name=service_name,
        system_prompt=system_prompt,
        api_key=api_key,
        openai_model=openai_model,
    )
    markdown_renderer = Renderer(
        markdown_justify,
        markdown_code_theme,
        markdown_hyperlinks,
        markdown_inline_code_lexer,
        markdown_inline_code_theme
    )

    messages = []
    if filename == "-":
        if os.path.exists(session_history_file):
            with open(session_history_file, "r") as f:
                lines = f.readlines()
                if lines:
                    filename = lines[-1].strip()
                    click.echo(
                        f"Resuming from previous session: {filename}",
                        file=sys.stderr
                    )
                else:
                    filename = None
        else:
            filename = None

    parser = Parser()

    if filename and os.path.exists(filename):
        with open(filename, "r") as f:
            messages = parser.parse(f.read())

    if sys.stdin.isatty():
        if not reverse:
            file_content = generate_file_content(messages)
            file_content = click.edit(
                text=f"{file_content}@@> user:\n\n",
                extension=session_file_ext
            )
            messages = parser.parse(file_content)
        else:
            reversed_messages_from_file = list(reversed(messages))
            file_content = generate_file_content(reversed_messages_from_file)
            file_content = click.edit(
                text=f"@@> user:\n\n{file_content}",
                extension=session_file_ext
            )
            messages = list(reversed(parser.parse(file_content)))
    else:
        messages = [*messages, *parser.parse(sys.stdin.read())]

    is_empty_message = (not messages
                        or not messages[-1].content.strip()
                        or messages[-1].role != "user")
    if is_empty_message:
        raise UsageError("Aborting request due to empty message")

    chatbot_response = client.create_chat_completion(messages)
    messages.append(chatbot_response)

    if no_rich or not sys.stdout.isatty():
        output = chatbot_response.content
    else:
        output = markdown_renderer.render(chatbot_response)

    if no_pager or not sys.stdout.isatty():
        click.echo(output)
    else:
        click.echo(output)
        click.echo_via_pager(output, color=True)

    if prompt_user:
        save = click.confirm("Save response?", default=True)
    elif assume_yes:
        save = True
    else:
        save = False

    if not filename and save:
        filename = generate_filename(
            client,
            summary_prompt,
            messages,
            session_file_ext
        )
        if current_directory:
            filename = os.path.join(os.curdir, filename)
        else:
            filename = os.path.join(session_file_location, filename)

    if filename and save:
        with open(filename, "w") as f:
            f.write(generate_file_content(messages))
            session_file_absolute_path = os.path.abspath(f.name)
        click.echo(f"Saved to {filename}", file=sys.stderr)
        open(session_history_file, "a").write(
            session_file_absolute_path + "\n"
        )


if __name__ == "__main__":
    main(auto_envvar_prefix="DOTCHATBOT")
