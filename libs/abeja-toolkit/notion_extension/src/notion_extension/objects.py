from typing import Any, Literal

from pydantic import BaseModel, Field

from .base import _Base
from .colors import BACKGROUND_COLORS, COLORS


class URL(BaseModel):
    url: str = Field(..., description="URL to link to")


class Text(BaseModel):
    content: str = Field(..., description="Text content")
    link: URL | None = Field(default=None, description="URL to link to")


class Annotations(BaseModel):
    bold: bool = Field(default=False, description="Whether the text is bold")
    italic: bool = Field(default=False, description="Whether the text is italic")
    strikethrough: bool = Field(default=False, description="Whether the text is strikethrough")
    underline: bool = Field(default=False, description="Whether the text is underlined")
    code: bool = Field(default=False, description="Whether the text is inline code")
    color: COLORS | BACKGROUND_COLORS | None = Field(
        default="default", description="Text color or background color"
    )


class DateContent(BaseModel):
    start: str = Field(..., description="Start date. Format: YYYY-MM-DD")
    end: str | None = Field(default=None, description="End date. Format: YYYY-MM-DD")
    time_zone: str | None = Field(default=None, description="Time zone")


class Date(_Base):
    type: Literal["date"] = Field(default="date", description="Date type. Always must be 'date'")
    content: DateContent = Field(..., description="Date object content")


class UserContent(BaseModel):
    object: Literal["user"] = Field(
        default="user", description="Object type. Always must be 'user'"
    )
    id: str = Field(..., description="User ID")


class User(_Base):
    type: Literal["user"] = Field(default="user", description="Mention type. Always must be 'user'")
    content: UserContent = Field(..., description="User object content")


class DatabaseContent(BaseModel):
    id: str = Field(..., description="Database ID")


class Database(_Base):
    type: Literal["database"] = Field(
        default="database", description="Mention type. Always must be 'database'"
    )
    content: DatabaseContent = Field(..., description="Database object content")


class LinkPreview(_Base):
    type: Literal["link_preview"] = Field(
        default="link_preview", description="Mention type. Always must be 'link_preview'"
    )
    content: URL = Field(..., description="Link preview object content")


class PageContent(BaseModel):
    id: str = Field(..., description="Page ID")


class Page(_Base):
    type: Literal["page"] = Field(default="page", description="Mention type. Always must be 'page'")
    content: PageContent = Field(..., description="Page object content")


class TemplateMentionDate(BaseModel):
    type: Literal["template_mention_date"] = Field(
        default="template_mention_date",
        description="Template mention type. Always must be 'template_mention_date'",
    )
    template_mention_date: Literal["today", "now"] = Field(
        ..., description="Template mention date. Must be 'today' or 'now'"
    )


class TemplateMentionUser(BaseModel):
    type: Literal["template_mention_user"] = Field(
        default="template_mention_user",
        description="Template mention type. Always must be 'template_mention_user'",
    )
    template_mention_user: Literal["me"] = Field(
        ..., description="Template mention user. Must be 'me'"
    )


class TemplateMention(_Base):
    type: Literal["template_mention"] = Field(
        default="template_mention",
        description="Mention type. Always must be 'template_mention'",
    )
    content: TemplateMentionDate | TemplateMentionUser = Field(
        ..., description="Template mention object content"
    )


MentionType = User | Database | LinkPreview | Page | TemplateMention


class EquationContent(BaseModel):
    expression: str = Field(..., description="Equation expression")


class Equation(_Base):
    type: Literal["equation"] = Field(
        default="equation", description="Object type. Always must be 'equation'"
    )
    content: EquationContent = Field(..., description="Equation object content")


class RichText(BaseModel):
    type: Literal["text", "mention", "equation"] = Field(
        ..., description="Rich text type. Must be 'text', 'mention', or 'equation'"
    )
    text: Text | None = Field(
        default=None,
        description="Text object content. If type is not 'text', this field must be None.",
    )
    mention: MentionType | dict[str, Any] | None = Field(
        default=None,
        description="Mention object content. If type is not 'mention', this field must be None.",
    )
    equation: EquationContent | None = Field(
        default=None,
        description="Equation object content. If type is not 'equation', this field must be None.",
    )
    annotations: Annotations | None = Field(default=None, description="Text annotations")
    plain_text: str | None = Field(default=None, description="Plain text content")
    href: str | None = Field(default=None, description="Hyperlink reference")


class BookmarkContent(BaseModel):
    url: str = Field(..., description="URL to bookmark")
    caption: list[RichText] | None = Field(default=None, description="Bookmark caption")


class Bookmark(_Base):
    type: Literal["bookmark"] = Field(
        default="bookmark", description="Object type. Always must be 'bookmark'"
    )
    content: BookmarkContent = Field(..., description="Bookmark object content")


class BreadCrumb(_Base):
    type: Literal["breadcrumb"] = Field(
        default="breadcrumb", description="Object type. Always must be 'breadcrumb'"
    )
    content: dict[str, Any] = Field(
        default={}, description="Breadcrumb object content. Always empty."
    )


class BulletedListItemContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )


class BulletedListItem(_Base):
    type: Literal["bulleted_list_item"] = Field(
        default="bulleted_list_item", description="Object type. Always must be 'bulleted_list_item'"
    )
    content: BulletedListItemContent = Field(..., description="Bulleted list item object content")


class NumberedListItemContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )


class NumberedListItem(_Base):
    type: Literal["numbered_list_item"] = Field(
        default="numbered_list_item", description="Object type. Always must be 'numbered_list_item'"
    )
    content: NumberedListItemContent = Field(..., description="Numbered list item object content")


class QuoteContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )


class Quote(_Base):
    type: Literal["quote"] = Field(
        default="quote", description="Object type. Always must be 'quote'"
    )
    content: QuoteContent = Field(..., description="Quote object content")


class ToDoContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )
    checked: bool = Field(default=False, description="Whether the to-do is checked.")


class ToDo(_Base):
    type: Literal["to_do"] = Field(
        default="to_do", description="Object type. Always must be 'to_do'"
    )
    content: ToDoContent = Field(..., description="To-do object content")


class ToggleContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )


class Toggle(_Base):
    type: Literal["toggle"] = Field(
        default="toggle", description="Object type. Always must be 'toggle'"
    )
    content: ToggleContent = Field(..., description="Toggle object content")


class Heading1Content(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    is_toggleable: bool | None = Field(default=None, description="Whether the heading is togglable")


class Heading1(_Base):
    type: Literal["heading_1"] = Field(
        default="heading_1", description="Object type. Always must be 'heading_1'"
    )
    content: Heading1Content = Field(..., description="Heading 1 object content")


class Heading2Content(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    is_toggleable: bool | None = Field(default=None, description="Whether the heading is togglable")


class Heading2(_Base):
    type: Literal["heading_2"] = Field(
        default="heading_2", description="Object type. Always must be 'heading_2'"
    )
    content: Heading2Content = Field(..., description="Heading 2 object content")


class Heading3Content(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    is_toggleable: bool | None = Field(default=None, description="Whether the heading is togglable")


class Heading3(_Base):
    type: Literal["heading_3"] = Field(
        default="heading_3", description="Object type. Always must be 'heading_3'"
    )
    content: Heading3Content = Field(..., description="Heading 3 object content")


class ParagraphContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    color: COLORS | BACKGROUND_COLORS = Field(
        default="default", description="Text color or background color"
    )
    children: BaseModel | None = Field(
        default=None, description="Nested block. This field is used for indentation."
    )


class Paragraph(_Base):
    type: Literal["paragraph"] = Field(
        default="paragraph", description="Object type. Always must be 'paragraph'"
    )
    content: ParagraphContent = Field(..., description="Paragraph object content")


class Divider(_Base):
    type: Literal["divider"] = Field(
        default="divider", description="Object type. Always must be 'divider'"
    )
    content: dict[str, Any] = Field(default={}, description="Divider object content. Always empty.")


class CodeContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="Rich text content")
    caption: list[RichText] | None = Field(default=None, description="Code caption")
    language: str | None = Field(
        default=None,
        description="Code language. See: https://developers.notion.com/reference/block#code",
    )


class Code(_Base):
    type: Literal["code"] = Field(default="code", description="Object type. Always must be 'code'")
    content: CodeContent = Field(..., description="Code object content")


class FileContent(BaseModel):
    url: str
    type: Literal["external", "file"] = Field(default="file")
    name: str | None = Field(default=None, description="File name")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        dump = super().model_dump(**kwargs)
        _type = dump.pop("type")
        name = dump.pop("name", None)

        if name:
            return {
                "type": _type,
                "file": dump,
                "name": name,
            }
        else:
            return {
                "type": _type,
                _type: dump,
            }


class File(_Base):
    type: Literal["file"] = Field(default="file", description="Object type. Always must be 'file'")
    content: FileContent = Field(..., description="File object content")


class Embed(_Base):
    type: Literal["embed"] = Field(
        default="embed", description="Object type. Always must be 'file'"
    )
    content: URL = Field(..., description="Embed object content")


BlockType = Literal[
    "block",
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "toggle",
    "child_page",
    "image",
    "video",
    "file",
    "pdf",
    "embed",
    "code",
    "equation",
    "divider",
    "callout",
    "quote",
    "collection_view",
    "table_of_contents",
    "breadcrumb",
    "bookmark",
    "unsupported",
    "file",
    "embed",
]

BlockContentTypes = (
    Paragraph
    | Heading1
    | Heading2
    | Heading3
    | BulletedListItem
    | NumberedListItem
    | LinkPreview
    | Equation
    | Bookmark
    | BreadCrumb
    | Code
    | Divider
    | Quote
    | ToDo
    | Toggle
    | Page
    | File
    | Embed
    # | RichText
)


class Block(BaseModel):
    content: BlockContentTypes = Field(..., description="Block content")

    def format(self) -> dict[str, Any]:
        return {
            "object": "block",
            **self.content.format(),
        }
