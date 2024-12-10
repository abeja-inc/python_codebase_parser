import re
from typing import Any, Literal

from pydantic import BaseModel

from .colors import BACKGROUND_COLORS, COLORS
from .factory import RichTextFactory
from .objects import (
    URL,
    Annotations,
    Bookmark,
    BookmarkContent,
    BreadCrumb,
    BulletedListItem,
    BulletedListItemContent,
    Code,
    CodeContent,
    Date,
    DateContent,
    Divider,
    Embed,
    Equation,
    EquationContent,
    File,
    FileContent,
    Heading1,
    Heading1Content,
    Heading2,
    Heading2Content,
    Heading3,
    Heading3Content,
    NumberedListItem,
    NumberedListItemContent,
    Page,
    PageContent,
    Paragraph,
    ParagraphContent,
    Quote,
    QuoteContent,
    RichText,
    Text,
    ToDo,
    ToDoContent,
    Toggle,
    ToggleContent,
    User,
    UserContent,
)
from .objects import Block as _Block


class BlockGroup:
    def __init__(
        self,
        block_type: str,
        text: str,
        indent_level: int,
        children: list["BlockGroup"] | None = None,
    ):
        self.block_type = block_type
        self.text = text
        self.indent_level = indent_level
        self.children = children or []

    def __repr__(self) -> str:
        if self.children:
            return f'Group(name="{self.block_type}", text={self.text}, indent={self.indent_level}, children={self.children})'
        else:
            return f'Group(name="{self.block_type}", text={self.text}, indent={self.indent_level})'


class Blocks(BaseModel):
    blocks: list[_Block]

    def format(self) -> list[dict[str, Any]]:
        return [block.format() for block in self.blocks]

    @staticmethod
    def _get_block_type_and_level(markdown: str, indent: int = 2) -> list[tuple[str, int, str]]:
        pattern_headings = re.compile(r"^(#+) ")
        pattern_bulleted_list_item = re.compile(r"^(-|\*) ")
        pattern_numbered_list_item = re.compile(r"^(\d+\.) ")
        pattern_expression = re.compile(r"^\$\$")
        pattern_codeblock = re.compile(r"^```")

        isin_equation = False
        isin_codeblock = False
        equation_text = ""
        codeblock_text = ""

        lines = markdown.split("\n")
        block_types = []
        for line in lines:
            # NOTE: Indent level of the notion block is determined by the relative ranking of the indentations.
            # So it is not always the same as the indent level in the markdown.
            indent_level = (len(line) - len(line.lstrip())) // indent
            line = line.strip()
            match_heading = pattern_headings.match(line.strip())
            match_bulleted_list_item = pattern_bulleted_list_item.match(line.strip())
            match_numbered_list_item = pattern_numbered_list_item.match(line.strip())
            match_expression = pattern_expression.match(line.strip())
            match_codeblock = pattern_codeblock.match(line.strip())

            if match_heading:
                heading_level = len(line) - len(line.lstrip("#"))
                block_types.append((f"heading_{heading_level}", indent_level, line.lstrip("# ")))
            elif match_bulleted_list_item:
                block_types.append(
                    ("bulleted_list_item", indent_level, line.lstrip("- *").rstrip("*"))
                )
            elif match_numbered_list_item:
                _, end = match_numbered_list_item.span()
                block_types.append(
                    (
                        "numbered_list_item",
                        indent_level,
                        line.strip()[end:],
                    )
                )
            elif match_expression:
                if isin_equation:
                    isin_equation = False
                    block_types.append(("equation", indent_level, equation_text))
                    equation_text = ""
                else:
                    isin_equation = True
            elif match_codeblock:
                if isin_codeblock:
                    isin_codeblock = False
                    block_types.append(("code", indent_level, codeblock_text))
                    codeblock_text = ""
                else:
                    isin_codeblock = True
            else:
                if isin_equation:
                    equation_text += line + "\n"
                elif isin_codeblock:
                    codeblock_text += line + "\n"
                else:
                    block_types.append(("paragraph", indent_level, line.strip()))
        return block_types

    @staticmethod
    def _group_lines(
        lines_block_type: list[tuple[str, int, str]],
    ) -> list[list[tuple[str, int, str]]]:
        groups = []
        current_group: list[tuple[str, int, str]] = []

        for line in lines_block_type:
            if line[1] == 0:
                if current_group:
                    groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)
        if current_group:
            groups.append(current_group)
        return groups

    @staticmethod
    def _markdownlink_to_rich_text(link: str) -> RichText:
        link_text = link.split("[")[1].split("]")[0]
        link_url = link.split("(")[1].split(")")[0]
        return RichTextFactory.text(content=link_text, link=link_url)

    @staticmethod
    def _text_to_richtext(text: str) -> list[RichText]:
        """Methods for generating inline complex rich text."""
        # page mentionとlinkがある場合は単一のRichText、それ以外は複数のRichText
        # page mentionは[*:page_id]、linkは[*](*)という形式で記述されている
        rich_texts = []
        page_mentions = re.finditer(r"\[([^\[\]:]+?):([^\[\]]+?)\]", text)
        link_matches = re.finditer(r"\[([^\[\]]+?)\]\(([^\s\)]+?)\)", text)
        inline_codes = re.finditer(r"`(.+?)`", text)
        inline_expressions = re.finditer(r"\$(.+?)\$", text)

        matches = []

        for link_match in link_matches:
            matches.append(("_markdownlink_to_rich_text", link_match.start(), link_match.end()))

        for inline_code in inline_codes:
            matches.append(("inline_code", inline_code.start(), inline_code.end()))

        for page_mention in page_mentions:
            matches.append(("page_mention", page_mention.start(), page_mention.end()))

        for inline_expression in inline_expressions:
            matches.append(("inline_equation", inline_expression.start(), inline_expression.end()))

        if len(matches) >= 1:
            matches = sorted(matches, key=lambda x: x[1])
            for i, match in enumerate(matches):
                if i == 0:
                    if match[1] != 0:
                        rich_texts.append(RichTextFactory.text(content=text[: match[1]]))
                else:
                    if matches[i - 1][2] != match[1]:
                        rich_texts.append(
                            RichTextFactory.text(content=text[matches[i - 1][2] : match[1]])
                        )

                if match[0] == "inline_code":
                    code = text[match[1] : match[2]].strip("`")
                    rich_texts.append(RichTextFactory.text(content=code, code=True, color="red"))
                elif match[0] == "page_mention":
                    page_mention_txt = text[match[1] : match[2]]
                    page_id = page_mention_txt.split(":")[1].strip("]")
                    rich_texts.append(RichTextFactory.page_mention(content=page_id))
                elif match[0] == "inline_equation":
                    expression = text[match[1] : match[2]].strip("$")
                    rich_texts.append(RichTextFactory.equation(content=expression))
                elif match[0] == "_markdownlink_to_rich_text":
                    link = text[match[1] : match[2]]
                    rich_texts.append(Blocks._markdownlink_to_rich_text(link))

            rich_texts.append(RichTextFactory.text(content=text[matches[-1][2] :]))

        else:
            rich_texts.append(RichTextFactory.text(content=text))

        return rich_texts

    @staticmethod
    def _build_hierarchy(group: list[tuple[str, int, str]]) -> BlockGroup:
        stack: list[tuple[int, BlockGroup]] = []
        root: BlockGroup
        for block_type, indent, text in group:
            g = BlockGroup(block_type=block_type, text=text, indent_level=indent)
            # Pop stack until finding a parent node with indent less than current
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if stack:
                _, parent_g = stack[-1]
                parent_g.children.append(g)
            else:
                root = g  # Current node is the root
            stack.append((indent, g))
        return root

    @staticmethod
    def _hierarchy_to_blocks(group: BlockGroup) -> _Block:
        blocks = []
        if group.children:
            for child in group.children:
                recurse = Blocks._hierarchy_to_blocks(child)
                blocks.append(recurse)
            rich_texts = Blocks._text_to_richtext(group.text)
            block: _Block = getattr(Block, f"{group.block_type}_from_rich_text")(
                rich_texts, children=Blocks(blocks=blocks)
            )
            return block
        else:
            if group.block_type.startswith("heading"):
                block_heading: _Block = getattr(Block, f"{group.block_type}")(group.text)
                return block_heading
            elif group.block_type == "equation":
                block_equation: _Block = getattr(Block, f"{group.block_type}")(group.text.strip())
                return block_equation
            elif group.block_type == "code":
                block_code: _Block = getattr(Block, f"{group.block_type}")(
                    group.text.strip(),
                    "python",  # TODO: Support other languages
                )
                return block_code
            else:
                rich_texts = Blocks._text_to_richtext(group.text)
                block_text: _Block = getattr(Block, f"{group.block_type}_from_rich_text")(
                    rich_texts
                )
                return block_text

    @classmethod
    def from_markdown(cls, text: str) -> "Blocks":
        """
        Convert markdown text to Notion Blocks.
        Supported markdown syntax:
            - Headings: #, ##, ###
            - Bulleted list: -, *
            - Numbered list: 1., 2., ...
            - Paragraph
            - Link
            - Page mention
            - Inline code
            - Inline equation
            - Code block (only Python)
            - Equation block

        Parameters
        ----------
        text : str
            The markdown text.

        Returns
        -------
        Blocks
            The Notion Blocks.
        """

        page_contents = []
        # Get block type and indent level for each line
        lines_block_type = cls._get_block_type_and_level(text)

        # Group lines by indent level
        grouped_lines_block_type = cls._group_lines(lines_block_type)

        for grouped_line in grouped_lines_block_type:
            # Build hierarchy from grouped lines based on indent level
            hierarchy = cls._build_hierarchy(grouped_line)

            # Convert hierarchy to blocks
            page_contents.append(cls._hierarchy_to_blocks(hierarchy))

        return Blocks(blocks=page_contents)


class Block:
    """
    A factory class to create Notion block objects.

    Methods
    -------
    heading_1(content: str, color: str = "default", is_toggleable: bool | None = None) -> Block:
        Create a heading 1 block.

    heading_2(content: str, color: str = "default", is_toggleable: bool | None = None) -> Block:
        Create a heading 2 block.

    heading_3(content: str, color: str = "default", is_toggleable: bool | None = None) -> Block:
        Create a heading 3 block.

    code(content: str, language: str, caption: str | None = None) -> Block:
        Create a code block.

    bulleted_list_item(content: str, children: Blocks | None = None, color: str = "default",
                       italic: bool = False, bold: bool = False, strikethrough: bool = False,
                       underline: bool = False, code: bool = False, text_color: str | None = None) -> Block:
        Create a bulleted list item block.

    bulleted_list_item_from_rich_text(rich_text: list[RichText], children: Blocks | None = None,
                                      color: str = "default") -> Block:
        Create a bulleted list item block from rich text.

    numbered_list_item(content: str, children: Blocks | None = None, color: str = "default",
                       italic: bool = False, bold: bool = False, strikethrough: bool = False,
                       underline: bool = False, code: bool = False, text_color: str | None = None) -> Block:
        Create a numbered list item block.

    numbered_list_item_from_rich_text(rich_text: list[RichText], children: Blocks | None = None,
                                        color: str = "default") -> Block:
        Create a numbered list item block from rich text.

    paragraph(content: str, link: str | None = None, children: Blocks | None = None,
              color: str = "default", bold: bool = False, italic: bool = False,
              strikethrough: bool = False, underline: bool = False, code: bool = False,
              text_color: str | None = None) -> Block:
        Create a paragraph block.

    paragraph_from_rich_text(rich_text: list[RichText], children: Blocks | None = None,
                             color: str = "default") -> Block:
        Create a paragraph block from rich text.

    page_mention(page_id: str) -> Block:
        Create a page mention block.

    user_mention(user_id: str) -> Block:
        Create a user mention block.

    date_mention(date: str) -> Block:
        Create a date mention block.

    equation(expression: str) -> Block:
        Create an equation block.

    bookmark(url: str, caption: str | None = None) -> Block:
        Create a bookmark block.

    breadcrumb() -> Block:
        Create a breadcrumb block.

    divider() -> _Block:
        Create a divider block.

    quote(content: str, children: Blocks | None = None, color: str = "default",
          bold: bool = False, italic: bool = False, strikethrough: bool = False,
          underline: bool = False, code: bool = False, text_color: str | None = None) -> Block:
        Create a quote block.

    todo(content: str, checked: bool = False, children: Blocks | None = None,
         color: str = "default", bold: bool = False, italic: bool = False,
         strikethrough: bool = False, underline: bool = False, code: bool = False,
         text_color: str | None = None) -> Block:
        Create a todo block.

    toggle(content: str, children: Blocks | None = None, color: str = "default",
              bold: bool = False, italic: bool = False, strikethrough: bool = False,
              underline: bool = False, code: bool = False, text_color: str | None = None) -> Block:
          Create a toggle block.
    """

    @staticmethod
    def heading_1(
        content: str,
        color: COLORS | BACKGROUND_COLORS = "default",
        is_toggleable: bool | None = None,
    ) -> _Block:
        """
        Create a heading 1 block.

        Parameters
        ----------
        content : str
            The text of the heading.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the heading. Default is "default".
        is_toggleable : bool | None, optional
            Whether the heading is togglable. Default is None.

        Returns
        -------
        Block
            The heading 1 block.
        """
        return _Block(
            content=Heading1(
                content=Heading1Content(
                    rich_text=[RichText(type="text", text=Text(content=content))],
                    color=color,
                    is_toggleable=is_toggleable,
                )
            )
        )

    @staticmethod
    def heading_2(
        content: str,
        color: COLORS | BACKGROUND_COLORS = "default",
        is_toggleable: bool | None = None,
    ) -> _Block:
        """
        Create a heading 2 block.

        Parameters
        ----------
        content : str
            The text of the heading.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the heading. Default is "default".
        is_toggleable : bool | None, optional
            Whether the heading is togglable. Default is None.

        Returns
        -------
        Block
            The heading 2 block.
        """
        return _Block(
            content=Heading2(
                content=Heading2Content(
                    rich_text=[RichText(type="text", text=Text(content=content))],
                    color=color,
                    is_toggleable=is_toggleable,
                )
            )
        )

    @staticmethod
    def heading_3(
        content: str,
        color: COLORS | BACKGROUND_COLORS = "default",
        is_toggleable: bool | None = None,
    ) -> _Block:
        """
        Create a heading 3 block.

        Parameters
        ----------
        content : str
            The text of the heading.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the heading. Default is "default".
        is_toggleable : bool | None, optional
            Whether the heading is togglable. Default is None.

        Returns
        -------
        Block
            The heading 3 block.
        """

        return _Block(
            content=Heading3(
                content=Heading3Content(
                    rich_text=[RichText(type="text", text=Text(content=content))],
                    color=color,
                    is_toggleable=is_toggleable,
                )
            )
        )

    @staticmethod
    def code(content: str, language: str, caption: str | None = None) -> _Block:
        """
        Create a code block.

        Parameters
        ----------
        content : str
            The content of the code block.
        language : str
            The language of the code block.
        caption : str | None, optional
            The caption of the code block. Default is None.

        Returns
        -------
        Block
            The code block
        """
        return _Block(
            content=Code(
                content=CodeContent(
                    rich_text=[RichText(type="text", text=Text(content=content))],
                    language=language,
                    caption=[RichText(type="text", text=Text(content=caption))]
                    if caption
                    else None,
                )
            )
        )

    @staticmethod
    def bulleted_list_item(
        content: str,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        italic: bool = False,
        bold: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a bulleted list item block.

        Parameters
        ----------
        content : str
            The text content of the bulleted list item.
        children : Blocks | None, optional
            The children of the bulleted list item. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the bulleted list item. Default is "default".
        italic : bool, optional
            Whether the content is italic. Default is False.
        bold : bool, optional
            Whether the content is bold. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : str | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The bulleted list item block.
        """
        return _Block(
            content=BulletedListItem(
                content=BulletedListItemContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content),
                            annotations=Annotations(
                                italic=italic,
                                bold=bold,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def bulleted_list_item_from_rich_text(
        rich_text: list[RichText],
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
    ) -> _Block:
        """
        Create a bulleted list item block from the list of rich text.
        This method is useful when you want to create a bulleted list item with complex rich text in the same block.

        Parameters
        ----------
        rich_text : list[RichText]
            The list of rich text.
        children : Blocks | None, optional
            The children of the bulleted list item. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the bulleted list item. Default is "default".

        Returns
        -------
        Block
            The bulleted list item block.
        """
        return _Block(
            content=BulletedListItem(
                content=BulletedListItemContent(
                    rich_text=rich_text,
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def numbered_list_item(
        content: str,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        italic: bool = False,
        bold: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a numbered list item block.

        Parameters
        ----------
        content : str
            The text content of the numbered list item.
        children : Blocks | None, optional
            The children of the numbered list item. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the numbered list item. Default is "default".
        italic : bool, optional
            Whether the content is italic. Default is False.
        bold : bool, optional
            Whether the content is bold. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : COLORS | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The numbered list item block.
        """
        return _Block(
            content=NumberedListItem(
                content=NumberedListItemContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content),
                            annotations=Annotations(
                                italic=italic,
                                bold=bold,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def numbered_list_item_from_rich_text(
        rich_text: list[RichText],
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
    ) -> _Block:
        """
        Create a numbered list item block from the list of rich text.
        This method is useful when you want to create a numbered list item with complex rich text in the same block.

        Parameters
        ----------
        rich_text : list[RichText]
            The list of rich text.
        children : Blocks | None, optional
            The children of the numbered list item. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the numbered list item. Default is "default".

        Returns
        -------
        Block
            The numbered list item block.
        """
        return _Block(
            content=NumberedListItem(
                content=NumberedListItemContent(
                    rich_text=rich_text,
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def paragraph(
        content: str,
        link: str | None = None,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a paragraph block.

        Parameters
        ----------
        content : str
            The text content of the paragraph.
        link : str | None, optional
            The overlayed link on the text. Default is None.
        children : Blocks | None, optional
            The children of the paragraph. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the paragraph. Default is "default".
        bold : bool, optional
            Whether the content is bold. Default is False.
        italic : bool, optional
            Whether the content is italic. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : COLORS | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The paragraph block.
        """
        return _Block(
            content=Paragraph(
                content=ParagraphContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content, link=URL(url=link) if link else None),
                            annotations=Annotations(
                                bold=bold,
                                italic=italic,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def paragraph_from_rich_text(
        rich_text: list[RichText],
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
    ) -> _Block:
        """
        Create a paragraph block from the list of rich text.
        This method is useful when you want to create a paragraph with complex paragpraph in the same block.

        Parameters
        ----------
        rich_text : list[RichText]
            The list of rich text.
        children : Blocks | None, optional
            The children of the paragraph. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the paragraph. Default is "default".

        Returns
        -------
        Block
            The paragraph block.
        """
        return _Block(
            content=Paragraph(
                content=ParagraphContent(
                    rich_text=rich_text,
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def page_mention(
        page_id: str,
    ) -> _Block:
        """
        Create a page mention block.

        Parameters
        ----------
        page_id : str
            The ID of the page to mention.

        Returns
        -------
        Block
            The page mention block.
        """
        return _Block(
            content=Paragraph(
                content=ParagraphContent(
                    rich_text=[
                        RichText(
                            type="mention",
                            mention=Page(
                                content=PageContent(
                                    id=page_id,
                                )
                            ).format(),
                        )
                    ],
                )
            )
        )

    @staticmethod
    def user_mention(
        user_id: str,
    ) -> _Block:
        """
        Create a user mention block.

        Parameters
        ----------
        user_id : str
            The ID of the user to mention.

        Returns
        -------
        Block
            The user mention block.
        """
        return _Block(
            content=Paragraph(
                content=ParagraphContent(
                    rich_text=[
                        RichText(
                            type="mention",
                            mention=User(
                                content=UserContent(
                                    id=user_id,
                                )
                            ).format(),
                        )
                    ],
                )
            )
        )

    @staticmethod
    def date_mention(
        date: str,
    ) -> _Block:
        """
        Create a date mention block.

        Parameters
        ----------
        date : str
            The date to mention.

        Returns
        -------
        Block
            The date mention block.
        """
        return _Block(
            content=Paragraph(
                content=ParagraphContent(
                    rich_text=[
                        RichText(
                            type="mention",
                            mention=Date(
                                content=DateContent(
                                    start=date,
                                )
                            ).format(),
                        )
                    ],
                )
            )
        )

    @staticmethod
    def equation(expression: str) -> _Block:
        """
        Create an equation block.

        Parameters
        ----------
        expression : str
            The expression of the equation.

        Returns
        -------
        Block
            The equation block.
        """
        return _Block(
            content=Equation(
                content=EquationContent(
                    expression=expression,
                )
            )
        )

    @staticmethod
    def bookmark(url: str, caption: str | None = None) -> _Block:
        """
        Create a bookmark block.

        Parameters
        ----------
        url : str
            The URL of the bookmark.
        caption : str | None, optional
            The caption of the bookmark. Default is None.

        Returns
        -------
        Block
            The bookmark block.
        """
        return _Block(
            content=Bookmark(
                content=BookmarkContent(
                    url=url,
                    caption=[RichText(type="text", text=Text(content=caption))]
                    if caption
                    else None,
                )
            )
        )

    @staticmethod
    def breadcrumb() -> _Block:
        """
        Create a breadcrumb block.

        Returns
        -------
        Block
            The breadcrumb block.
        """
        return _Block(content=BreadCrumb())

    @staticmethod
    def divider() -> _Block:
        """
        Create a divider block.

        Returns
        -------
        Block
            The divider block.
        """
        return _Block(content=Divider(content={}))

    @staticmethod
    def quote(
        content: str,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a quote block.

        Parameters
        ----------
        content : str
            The text content of the quote.
        children : Blocks | None, optional
            The children of the quote. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the quote. Default is "default".
        bold : bool, optional
            Whether the content is bold. Default is False.
        italic : bool, optional
            Whether the content is italic. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : COLORS | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The quote block.
        """

        return _Block(
            content=Quote(
                content=QuoteContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content),
                            annotations=Annotations(
                                bold=bold,
                                italic=italic,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def todo(
        content: str,
        checked: bool = False,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a todo block.

        Parameters
        ----------
        content : str
            The text content of the todo.
        checked : bool, optional
            Whether the todo is checked. Default is False.
        children : Blocks | None, optional
            The children of the todo. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the todo. Default is "default".
        bold : bool, optional
            Whether the content is bold. Default is False.
        italic : bool, optional
            Whether the content is italic. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : COLORS | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The todo block.
        """
        return _Block(
            content=ToDo(
                content=ToDoContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content),
                            annotations=Annotations(
                                bold=bold,
                                italic=italic,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    checked=checked,
                    color=color,
                )
            )
        )

    @staticmethod
    def toggle(
        content: str,
        children: Blocks | None = None,
        color: COLORS | BACKGROUND_COLORS = "default",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        text_color: COLORS | None = None,
    ) -> _Block:
        """
        Create a toggle block.

        Parameters
        ----------
        content : str
            The text content of the toggle.
        children : Blocks | None, optional
            The children of the toggle. Default is None.
        color : COLORS | BACKGROUND_COLORS, optional
            The text or background color of the toggle. Default is "default".
        bold : bool, optional
            Whether the content is bold. Default is False.
        italic : bool, optional
            Whether the content is italic. Default is False.
        strikethrough : bool, optional
            Whether the content is strikethrough. Default is False.
        underline : bool, optional
            Whether the content is underlined. Default is False.
        code : bool, optional
            Whether the content is inline code. Default is False.
        text_color : COLORS | None, optional
            The color of the text. Default is None.

        Returns
        -------
        Block
            The toggle block.
        """
        return _Block(
            content=Toggle(
                content=ToggleContent(
                    rich_text=[
                        RichText(
                            type="text",
                            text=Text(content=content),
                            annotations=Annotations(
                                bold=bold,
                                italic=italic,
                                strikethrough=strikethrough,
                                underline=underline,
                                code=code,
                                color=text_color,
                            ),
                        )
                    ],
                    children=children,
                    color=color,
                )
            )
        )

    @staticmethod
    def embed(
        url: str,
    ) -> _Block:
        """
        Create a embed block.

        Parameters
        ----------
        url : str
            The URL of the embed.

        Returns
        -------
        Block
            The file block.
        """

        return _Block(
            content=Embed(
                content=URL(
                    url=url,
                ),
            )
        )

    @staticmethod
    def file(
        url: str,
        type: Literal["external", "file"],
        name: str | None = None,
    ) -> _Block:
        """
        Create a file block.

        Parameters
        ----------
        url : str
            The URL of the file.
        type : Literal["external", "file"]
            The type of the file. "external" or "file".

        Returns
        ---------
        Block
            The file block.
        """

        return _Block(
            content=File(
                content=FileContent(
                    url=url,
                    type=type,
                    name=name,
                ),
            )
        )
