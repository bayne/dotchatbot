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
