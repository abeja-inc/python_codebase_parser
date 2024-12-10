from typing import Any, Literal

from pydantic import BaseModel, Field

from .colors import BACKGROUND_COLORS, COLORS
from .objects import (
    Annotations,
    RichText,
    Text,
)


class _Property(BaseModel):
    name: str
    type: str
    content: Any

    def format(self) -> dict[str, Any]:
        raise NotImplementedError


class TitlePropertyContent(BaseModel):
    text: Text = Field(..., description="The text content of the title.")


class TitleProperty(_Property):
    type: Literal["title"] = Field(
        default="title", description="The type of the property. Always 'title'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: TitlePropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = [self.content.model_dump(exclude_none=True)]
        return {self.name: {self.type: contents}}


class StatusPropertyContent(BaseModel):
    name: str | None = Field(None, description="The name of the status.")


class StatusProperty(_Property):
    type: Literal["status"] = Field(
        default="status", description="The type of the property. Always 'status'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: StatusPropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = self.content.model_dump(exclude_none=True)

        return {self.name: {self.type: contents}}


class DescriptionPropertyContent(BaseModel):
    rich_text: list[RichText] = Field(..., description="The rich text content of the description.")


class DescriptionProperty(_Property):
    type: Literal["rich_text"] = Field(
        default="rich_text", description="The type of the property. Always 'rich_text'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: DescriptionPropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        rich_text = self.content.model_dump(exclude_none=True)["rich_text"]
        return {self.name: {self.type: rich_text}}


class CheckboxPropertyContent(BaseModel):
    checkbox: bool = Field(
        default=False,
        description="The boolean value of the checkbox. If None, the checkbox is unchecked.",
    )


class CheckboxProperty(_Property):
    type: Literal["checkbox"] = Field(
        default="checkbox", description="The type of the property. Always 'checkbox'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: CheckboxPropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = self.content.model_dump(exclude_none=True)

        return {self.name: contents}


class SelectPropertyContent(BaseModel):
    name: str | None = Field(None, description="The name of the select option.")


class SelectProperty(_Property):
    type: Literal["select"] = Field(
        default="select", description="The type of the property. Always 'select'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: SelectPropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = self.content.model_dump(exclude_none=True)

        return {self.name: {self.type: contents}}


class MultiSelectProperty(_Property):
    type: Literal["multi_select"] = Field(
        default="multi_select", description="The type of the property. Always 'multi_select'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: list[SelectPropertyContent] = Field(..., description="The options of the property.")

    def format(self) -> dict[str, Any]:
        return {
            self.name: {
                self.type: [_content.model_dump(exclude_none=True) for _content in self.content]
            }
        }


class URLPropertyContent(BaseModel):
    url: str | None = Field(None, description="The URL of the link.")


class URLProperty(_Property):
    type: Literal["url"] = Field(
        default="url", description="The type of the property. Always 'url'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: URLPropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = self.content.model_dump(exclude_none=True)

        return {self.name: contents}


class DatePropertyContent(BaseModel):
    start: str = Field(..., description="The start date of the date property.")
    end: str | None = Field(default=None, description="The end date of the date property.")


class DateProperty(_Property):
    type: Literal["date"] = Field(
        default="date", description="The type of the property. Always 'date'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: DatePropertyContent = Field(..., description="The content of the property.")

    def format(self) -> dict[str, Any]:
        contents = self.content.model_dump(exclude_none=True)

        return {self.name: {self.type: contents}}


class PeoplePropertyContent(BaseModel):
    people: dict[str, Any] = Field(..., description="The notion user object.")


class PeopleProperty(_Property):
    type: Literal["people"] = Field(
        default="people", description="The type of the property. Always 'people'."
    )
    name: str = Field(..., description="The name of the property on the DB.")
    content: list[PeoplePropertyContent] = Field(description="The list of the users.")

    def format(self) -> dict[str, Any]:
        contents = [content.people for content in self.content]

        return {self.name: {self.type: contents}}


PropertyType = (
    TitleProperty
    | StatusProperty
    | DescriptionProperty
    | CheckboxProperty
    | SelectProperty
    | MultiSelectProperty
    | URLProperty
    | DateProperty
    | PeopleProperty
)


class Properties(BaseModel):
    properties: list[PropertyType] = Field(..., description="The list of properties.")

    def format(self) -> dict[str, Any]:
        output = {}
        for prop in self.properties:
            output.update(prop.format())
        return output


class Property:
    """
    A factory class to create property objects for the Notion database.

    Methods
    -------
    title(name: str, text: str)
        Create a title property.
    status(name: str, status: str)
        Create a status property.
    description(name: str, text: str, bold: bool = False, italic: bool = False, strikethrough: bool = False, underline: bool = False, code: bool = False, color: COLORS | BACKGROUND_COLORS | None = "default")
        Create a description property.
    checkbox(name: str, checkbox: bool | None = False)
        Create a checkbox property.
    select(name: str, value: str)
        Create a select property.
    multi_select(name: str, values: list[str])
        Create a multi-select property.
    url(name: str, url: str)
        Create a URL property.
    date(name: str, start: str, end: str | None = None)
        Create a date property.
    people(name: str, people: list[dict])
        Create a people property.
    """

    @staticmethod
    def title(name: str, text: str) -> TitleProperty:
        """
        Set a title property.

        Parameters
        ----------
        name : str
            The name of the property.
        text : str
            The text content of the title.

        Returns
        -------
        TitleProperty
            The title property object.
        """
        return TitleProperty(name=name, content=TitlePropertyContent(text=Text(content=text)))

    @staticmethod
    def status(name: str, status: str | None = None) -> StatusProperty:
        """
        Set a status property.

        Parameters
        ----------
        name : str
            The name of the property.
        status : str
            The name of the status.
        """
        return StatusProperty(name=name, content=StatusPropertyContent(name=status))

    @staticmethod
    def description(
        name: str,
        text: str,
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        color: COLORS | BACKGROUND_COLORS | None = "default",
    ) -> DescriptionProperty:
        """
        Set a description property.

        Parameters
        ----------
        name : str
            The name of the property.
        text : str
            The text content of the description.
        bold : bool, optional
            Whether the text is bold or not, by default False.
        italic : bool, optional
            Whether the text is italic or not, by default False.
        strikethrough : bool, optional
            Whether the text is strikethrough or not, by default False.
        underline : bool, optional
            Whether the text is underlined or not, by default False.
        code : bool, optional
            Whether the text is code or not, by default False.
        color : COLORS | BACKGROUND_COLORS | None, optional
            The color of the text, by default "default".

        Returns
        -------
        DescriptionProperty
            The description property
        """
        return DescriptionProperty(
            name=name,
            content=DescriptionPropertyContent(
                rich_text=[
                    RichText(
                        type="text",
                        text=Text(content=text),
                        annotations=Annotations(
                            bold=bold,
                            italic=italic,
                            strikethrough=strikethrough,
                            underline=underline,
                            code=code,
                            color=color,
                        ),
                    )
                ]
            ),
        )

    @staticmethod
    def checkbox(name: str, checkbox: bool = False) -> CheckboxProperty:
        """
        Set a checkbox property.

        Parameters
        ----------
        name : str
            The name of the property.
        checkbox : bool, optional
            The boolean value of the checkbox. If None, the checkbox is unchecked, by default False.

        Returns
        -------
        CheckboxProperty
            The checkbox property object.
        """
        return CheckboxProperty(name=name, content=CheckboxPropertyContent(checkbox=checkbox))

    @staticmethod
    def select(name: str, value: str) -> SelectProperty:
        """
        Set a select property.

        Parameters
        ----------
        name : str
            The name of the property.
        value : str
            The name of the select option.

        Returns
        -------
        SelectProperty
            The select property object.
        """
        return SelectProperty(name=name, content=SelectPropertyContent(name=value))

    @staticmethod
    def multi_select(name: str, values: list[str]) -> MultiSelectProperty:
        """
        Set a multi-select property.

        Parameters
        ----------
        name : str
            The name of the property.
        values : list[str]
            The list of the select options.

        Returns
        -------
        MultiSelectProperty
            The multi-select property object.
        """
        return MultiSelectProperty(
            name=name, content=[SelectPropertyContent(name=value) for value in values]
        )

    @staticmethod
    def url(name: str, url: str) -> URLProperty:
        """
        Set a URL property.

        Parameters
        ----------
        name : str
            The name of the property.
        url : str
            The URL of the link.

        Returns
        -------
        URLProperty
            The URL property object.
        """
        return URLProperty(name=name, content=URLPropertyContent(url=url))

    @staticmethod
    def date(name: str, start: str, end: str | None = None) -> DateProperty:
        """
        Set a date property.

        Parameters
        ----------
        name : str
            The name of the property.
        start : str
            The start date of the date property.
        end : str, optional
            The end date of the date property, by default None.

        Returns
        -------
        DateProperty
            The date property object.
        """
        return DateProperty(name=name, content=DatePropertyContent(start=start, end=end))

    @staticmethod
    def people(name: str, people: list[dict[str, Any]]) -> PeopleProperty:
        """
        Set a people property.

        Parameters
        ----------
        name : str
            The name of the property.
        people: list[dict]
            The list of the user objects

        Returns
        ----------
        PeopleProperty
            The people property object
        """
        return PeopleProperty(
            name=name, content=[PeoplePropertyContent(people=person) for person in people]
        )
