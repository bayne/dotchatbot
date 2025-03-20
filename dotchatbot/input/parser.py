from typing import List
from typing import Optional

from lark import Lark

from dotchatbot.input.transformer import Message
from dotchatbot.input.transformer import SectionTransformer

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


class Parser:
    def __init__(self) -> None:
        self.lark = Lark(GRAMMAR, parser='lalr')
        self.transformer = SectionTransformer()

    def parse(self, document: Optional[str]) -> List[Message]:
        if not document or not document.strip():
            return []
        tree = self.lark.parse(document)
        return self.transformer.transform(tree)
