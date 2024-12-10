import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

from .data import Cell
from .utils import decode_image


class NotebookExtractor:
    @staticmethod
    def _get_stream_content(output: dict[str, Any]) -> tuple[str, str]:
        return "text/plain", "".join(output.get("text", []))
        # return {"mime_type": "text/plain", "content": "".join(output.get("text", []))}

    @staticmethod
    def _get_execute_result_content(
        output: dict[str, Any],
    ) -> tuple[str, str | Image.Image] | tuple[None, None]:
        output_data = output.get("data", {})
        if "image/jpeg" in output_data:
            return "image/jpeg", decode_image(output_data["image/jpeg"])
            # return {"mime_type": "image/jpeg", "content": decode_image(output_data["image/jpeg"])}
        if "image/png" in output_data:
            return "image/png", decode_image(output_data["image/png"])
            # return {"mime_type": "image/png", "content": decode_image(output_data["image/png"])}
        elif "text/plain" in output_data:
            return "text/plain", "".join(output_data["text/plain"])
            # return {"mime_type": "text/plain", "content": "".join(output_data["text/plain"])}
        else:
            return None, None

    @staticmethod
    def _get_display_data_content(
        output: dict[str, Any],
    ) -> tuple[str, str | Image.Image] | tuple[None, None]:
        output_data = output.get("data", {})
        image_keys = [key for key in output_data.keys() if "image" in key]
        if "image/jpeg" in image_keys:
            return "image/jpeg", decode_image(output_data["image/jpeg"])
            # return {"mime_type": "image/jpeg", "content": decode_image(output_data["image/jpeg"])}

        elif "image/png" in image_keys:
            return "image/png", decode_image(output_data["image/png"])
            # return {"mime_type": "image/png", "content": decode_image(output_data["image/png"])}

        else:
            return None, None

    @staticmethod
    def _get_comments_in_code(code: str) -> str:
        pattern_hash_in_literal = re.compile(r"(\"|')+(#)+(\s)*(.+)(\"|')+(\n)*")
        pattern_hash = re.compile(r"(\"|')*(#)+(\s)*(.+)(\"|')*(\n)*")

        groups = []
        for _match in pattern_hash.finditer(code):
            group = _match.group()
            if not pattern_hash_in_literal.match(group):
                st, en = _match.span()
                groups.append((st, en - 1))

        # print(code, groups)
        comments = ""
        for st, en in groups:
            comments += code[st:en].strip(" #") + "\n"

        return comments

    @staticmethod
    def extract(notebook_path: str | Path) -> list[Cell]:
        """
        Extract markdown and code cells from a Jupyter notebook.

        Parameters
        ----------
        notebook_path : str | Path
            Path to the Jupyter notebook file.

        Returns
        -------
        Cell
            A list of cells containing the extracted markdown and code cells.
        """
        with open(notebook_path, "r") as f:
            notebook_data = json.load(f)

        outputs: list[Cell] = []
        is_target = False
        for cell in notebook_data.get("cells", []):
            cell_type = cell["cell_type"]
            if cell_type == "markdown":
                source = cell.get("source", [])

                if source:
                    markdown = "".join(source)
                    if not is_target and markdown == "# ToNotion":
                        is_target = True
                        continue

                    if is_target:
                        outputs.append(
                            Cell(
                                type="markdown",
                                mime_type="text/markdown",
                                text=markdown,
                            )
                        )

            elif cell_type == "code":
                if not is_target:
                    continue

                # source = cell.get("source", [])
                # if source:
                #     code = "".join(source)
                #     outputs.append(
                #         Cell(
                #             type="code",
                #             mime_type="text/markdown",
                #             text=NotebookExtractor._get_comments_in_code(code),
                #         )
                #     )
                # outputs.append(
                #     {
                #         "type": "code",
                #         "mime_type": "application/x-python",
                #         "content": code,
                #     }
                # )

                mime_type: str | None
                content: str | Image.Image | None
                for output in cell.get("outputs", []):
                    output_type = output["output_type"]

                    # 標準出力
                    if output_type == "stream":
                        mime_type, content = NotebookExtractor._get_stream_content(output)
                    # セルの実行結果
                    elif output_type == "execute_result":
                        mime_type, content = NotebookExtractor._get_execute_result_content(output)
                    # 画像やグラフなどの表示データ
                    elif output_type == "display_data":
                        mime_type, content = NotebookExtractor._get_display_data_content(output)
                    else:
                        continue

                    if content and mime_type:
                        if isinstance(content, Image.Image):
                            outputs.append(
                                Cell(
                                    type="output",
                                    mime_type=mime_type,
                                    image=content,
                                )
                            )
                        else:
                            outputs.append(
                                Cell(
                                    type="output",
                                    mime_type=mime_type,
                                    text=content,
                                )
                            )

        return outputs
