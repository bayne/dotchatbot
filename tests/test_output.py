from unittest.mock import MagicMock

from pytest import mark

from dotchatbot.output.file import generate_filename


@mark.parametrize(
    "summary,expected",
    [("Test Filename", "test-filename-00000.dcb"), (
        "Test Filename Some's Invalid!",
        "test-filename-somes-invalid-00000.dcb"), (
        "   Test Filename Some's Invalid!   ",
        "test-filename-somes-invalid-00000.dcb"), ]
)
def test_generate_filename(summary: str, expected: str) -> None:
    mock_client = MagicMock()
    mock_client.create_chat_completion.return_value.content = summary

    assert generate_filename(
        mock_client, 'Summarize', [], '.dcb'
    ) == expected
