from typing import Literal

from PIL import Image
from pydantic import BaseModel, ConfigDict


class Cell(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal["code", "markdown", "output"]
    mime_type: str
    text: str | None = None
    image: Image.Image | None = None
