from typing import Any

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: str
    content: BaseModel | dict[str, Any]

    def format(self) -> dict[str, Any]:
        if isinstance(self.content, dict):
            return {
                "type": self.type,
                self.type: self.content,
            }
        else:
            contents = self.content.model_dump(exclude={"children"}, exclude_none=True)
            if hasattr(self.content, "children") and self.content.children:
                children_contents = self.content.children.format()
                contents["children"] = children_contents

            return {
                "type": self.type,
                self.type: contents,
            }
