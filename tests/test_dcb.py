import os
from typing import Any
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from dotchatbot.dcb import dotchatbot


@pytest.fixture
def runner() -> Generator[CliRunner, Any, None]:
    """Fixture for setting up the CliRunner."""
    runner = CliRunner(
        env={
            "DOTCHATBOT_CONFIG": "test.toml"  # empty file to test defaults
        }
    )
    with runner.isolated_filesystem() as dir:
        path = os.path.join(dir, "test.toml")
        open(path, "w").close()
        yield runner


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.client.factory.create_client')
def test_dcb_no_arguments_should_fail(
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test running dcb with no args fails."""
    result = runner.invoke(dotchatbot, [])
    assert result.exit_code != 0
    assert "Error" in result.output


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.client.factory.create_client')
def test_dcb_help_option(
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test that the help option displays without error."""
    result = runner.invoke(dotchatbot, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.client.factory.create_client')
def test_dcb_invalid_service_name(
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test invalid service name fails."""
    result = runner.invoke(
        dotchatbot, ["--service-name", "InvalidService", "-y"]
    )
    assert result.exit_code == 2
    assert "Invalid value for '--service-name" in str(result.output)


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.dcb.create_client')
def test_dcb_valid_execution(
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test running dcb with valid parameters."""
    mock_get_api_key.return_value = 'fake_api_key'
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = 'Hello!'
    mock_message.role = 'assistant'
    mock_client.create_chat_completion.return_value = mock_message

    result = runner.invoke(
        dotchatbot,
        [
            '-y',
            '--openai-model',
            'gpt-4o',
        ],
        input='Hello!\n'
    )
    # assert result.exit_code == 0
    assert "Saved to" in result.output
    mock_get_api_key.assert_called_with('OpenAI')
    mock_create_client.assert_called_with(
        service_name='OpenAI',
        system_prompt='You are a helpful assistant.',
        api_key='fake_api_key',
        openai_model='gpt-4o',
        anthropic_model='claude-3-sonnet-latest',
        anthropic_max_tokens=16384,
        google_model='gemini-2.5-flash-lite'
    )


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.client.factory.create_client')
def test_dcb_assume_yes_and_no_fails(
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test that using -y and -n together fails."""
    result = runner.invoke(dotchatbot, ['-y', '-n'])
    assert result.exit_code != 0
    assert (
        "--assume-yes and --assume-no are mutually exclusive" in result.output)


@patch('dotchatbot.dcb._get_api_key')
@patch('dotchatbot.dcb.create_client')
@patch('os.path.exists', return_value=True)
@patch(
    'builtins.open', new_callable=mock_open, read_data=b"@@> user:\nHello\n"
)
def test_dcb_resume_session(
    mock_open: MagicMock,
    mock_exists: MagicMock,
    mock_create_client: MagicMock,
    mock_get_api_key: MagicMock,
    runner: CliRunner
) -> None:
    """Test resuming a previous session using '-'."""
    mock_get_api_key.return_value = 'fake_api_key'
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = 'Hello again!'
    mock_message.role = 'assistant'
    mock_client.create_chat_completion.return_value = mock_message

    result = runner.invoke(dotchatbot, ['-y', '-'])
    assert "Resuming from previous session:" in result.output
