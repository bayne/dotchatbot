from typing import Optional, List

from lark import Lark

from dotchatbot.parser.transformer import SectionTransformer, Message

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
transformer = SectionTransformer()


def parse(document: Optional[str]) -> List[Message]:
    if not document or not document.strip():
        return []
    tree = parser.parse(document)
    return transformer.transform(tree)
