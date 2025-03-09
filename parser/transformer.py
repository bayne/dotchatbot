from dataclasses import dataclass

from lark import Transformer

@dataclass(repr=True)
class Message:
    role: str
    content: str

class SectionTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def start(self, items):
        if items[0].data == "content":
            return [Message(role="user", content="".join(items[0].children))]

        items = map(lambda item: item.children, items)
        return [Message(role=role, content="".join(content.children)) for role, content in items]

    def header(self, items):
        return [i.value for i in items if i.type == "ROLE"][0]

    def line_without_header(self, items):
        return items[0].value