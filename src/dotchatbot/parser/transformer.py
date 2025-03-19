from dataclasses import dataclass
from typing import List, Tuple, TypeGuard, Literal, get_args

from lark import Transformer, Tree, Token

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str


def _content_type_guard(items: List[Tree | str]) -> TypeGuard[List[str]]:
    return all(map(lambda item: type(item) is str, items))


def _join(items: List[Tree | str]) -> str:
    if not _content_type_guard(items):
        raise TypeError("Invalid content")
    return "".join(items)


def _section_type_guard(
        items: List[List[Tree | str]]
) -> TypeGuard[List[Tuple[Role, Tree]]]:
    return all(
        map(
            lambda item: item[0] in get_args(Role) and type(item[1]) is Tree,
            items
        )
    )


class SectionTransformer(Transformer):
    def __init__(self) -> None:
        super().__init__()

    def start(self, items: List[Tree]) -> List[Message]:
        first_item: Tree = items[0]
        if first_item.data == "content":
            return [Message(role="user", content=_join(first_item.children))]

        items: List[List[Tree | str]] = list(
            map(lambda item: item.children, items)
        )
        if not _section_type_guard(items):
            raise TypeError("Invalid section")
        return [
            Message(
                role=role,
                content=_join(content.children)
            ) for role, content in items
        ]

    def header(self, items: List[Token]) -> List[str]:
        return [i.value for i in items if i.type == "ROLE"][0]

    def line_without_header(self, items: List[Token]) -> str:
        return items[0].value
