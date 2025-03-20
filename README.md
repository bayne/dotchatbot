# dotchatbot

[![PyPI - Version](https://img.shields.io/pypi/v/dotchatbot.svg)](https://pypi.org/project/dotchatbot)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dotchatbot.svg)](https://pypi.org/project/dotchatbot)

A practitioners approach of working with chat-based LLMs

![Demo of dotchatbot](demo.gif)

-----

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features

- File-based sessions
- Markdown output rendering via `rich`
- Session history and session resuming by just passing `-`
- Automatic filenames via prompting

## Installation

```console
pipx install dotchatbot
```

## Usage

```
Usage: dcb [OPTIONS] [FILENAME]

  Starts a session with the chatbot, resume by providing FILENAME. Provide - for
  FILENAME to use the previous session (stored in SESSION_HISTORY_FILE).

Options:
  -s, --service-name TEXT       The chatbot provider service name  [default:
                                OpenAI]
  -p, --system-prompt TEXT      The default system prompt to use  [default: You
                                are a helpful assistant.]
  --no-pager                    Do not output using pager
  --no-rich                     Do not output using rich
  -r, --reverse                 Reverse the conversation in the editor
  -y, --assume-yes              Automatic yes to prompts; assume "yes" as answer
                                to all prompts and run non-interactively.
  -n, --assume-no               Automatic no to prompts; assume "no" as answer
                                to all prompts and run non-interactively.
  -c, --current-directory       Use the current directory as the session file
                                location
  --session-history-file TEXT   The file where the session history is stored
                                [default:
                                /home/bpayne/.config/dotchatbot/.dotchatbot-
                                history]
  --session-file-location TEXT  The location where session files are stored
                                [default:
                                /home/bpayne/.config/dotchatbot/sessions]
  --session-file-ext TEXT       The extension to use for session files
                                [default: .dcb]
  --summary-prompt TEXT         The prompt to use for the summary (for building
                                the filename for the session)  [default: Given
                                the conversation so far, summarize it in just 4
                                words. Only respond with these 4 words]

OpenAI options:
  --openai-model     [default: gpt-4o]

Markdown options:
  --markdown-justify [default|left|center|right|full]
                              [default: default]
  --markdown-code-theme TEXT  [default: monokai]
  --markdown-hyperlinks
  --markdown-inline-code-lexer TEXT
  --markdown-inline-code-theme TEXT

Other options:
  --time / --no-time        Measure and print elapsed execution time.  [default:
                            no-time]
  --color, --ansi / --no-color, --no-ansi
                            Strip out all colors and all ANSI codes from output.
                            [default: color]
  -C, --config CONFIG_PATH  Location of the configuration file. Supports glob
                            pattern of local path and remote URL.  [default:
                            ~/.config/dcb/*.{toml,yaml,yml,json,ini,xml}]
  --show-params             Show all CLI parameters, their provenance, defaults
                            and value, then exit.
  --verbosity LEVEL         Either CRITICAL, ERROR, WARNING, INFO, DEBUG.
                            [default: WARNING]
  -v, --verbose             Increase the default WARNING verbosity by one level
                            for each additional repetition of the option.
                            [default: 0]
  --version                 Show the version and exit.
  -h, --help                Show this message and exit.
```

## License

`dotchatbot` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
