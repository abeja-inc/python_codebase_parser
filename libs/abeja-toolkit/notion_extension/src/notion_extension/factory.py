from .colors import BACKGROUND_COLORS, COLORS
from .objects import URL, Annotations, EquationContent, Page, PageContent, RichText, Text


class RichTextFactory:
    """This factory class is used to create RichText objects.
    The RichText object is used to represent the text content of a Notion block.
    """

    @staticmethod
    def text(
        content: str,
        link: str | None = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        code: bool = False,
        color: COLORS | BACKGROUND_COLORS | None = "default",
    ) -> RichText:
        """Create a RichText object with text type.

        Parameters
        ----------
        content : str
            The content of the text.
        link : str, optional
            The URL link of the text, by default None.
        bold : bool, optional
            Whether the text is bold, by default False.
        italic : bool, optional
            Whether the text is italic, by default False.
        underline : bool, optional
            Whether the text is underlined, by default False.
        strikethrough : bool, optional
            Whether the text is strikethrough, by default False.
        code : bool, optional
            Whether the text is code, by default False.
        color : COLORS | BACKGROUND_COLORS | None, optional
            The color of the text, by default "default".

        Returns
        -------
        RichText
            The RichText object with text type.
        """

        return RichText(
            type="text",
            text=Text(content=content, link=URL(url=link) if link else None),
            annotations=Annotations(
                bold=bold,
                italic=italic,
                underline=underline,
                strikethrough=strikethrough,
                code=code,
                color=color,
            ),
        )

    @staticmethod
    def page_mention(
        content: str,
    ) -> RichText:
        """Create a RichText object with mention type.

        Parameters
        ----------
        content : str
            The content of the mention.

        Returns
        -------
        RichText
            The RichText object with mention type.
        """
        return RichText(
            type="mention",
            mention=Page(content=PageContent(id=content)).format(),
        )

    @staticmethod
    def equation(
        content: str,
    ) -> RichText:
        """Create a RichText object with text type.

        Parameters
        ----------
        content : str
            The content of the equation.

        Returns
        -------
        RichText
            The RichText object with text type.
        """

        return RichText(
            type="equation",
            equation=EquationContent(expression=content),
        )
