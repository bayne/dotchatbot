from pytest import fixture
from pytest import mark

from dotchatbot.input.parser import Parser
from dotchatbot.input.transformer import Message


@fixture
def parser() -> Parser:
    return Parser()


@mark.parametrize(
    "input,expected",
    [
        (
            "",
            []
        ),
        (
            "some content\n",
            [
                Message(role="user", content="some content\n"),
            ]
        ),
        (
            "@@> user:\n"
            "test\n"
            "this\n"
            "is\n"
            "a\n"
            "test\n",
            [
                Message(role="user", content="test\nthis\nis\na\ntest\n"),
            ]
        ),

        (
            "@@> user:\n"
            "one\n"
            "@@> assistant:\n"
            "two\n"
            "@@> user:\n"
            "three\n",
            [
                Message(role="user", content="one\n"),
                Message(role="assistant", content="two\n"),
                Message(role="user", content="three\n"),
            ],
        )
    ]
)
def test_parser(parser: Parser, input: str, expected:  list[Message]) -> None:
    assert parser.parse(input) == expected
