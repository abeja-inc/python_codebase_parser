import logging
from pathlib import Path

from google.auth import default
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from notion_extension import Block, Blocks, Client, Properties, make_batch

from .data import Cell
from .extractor import NotebookExtractor
from .utils import pil2bytes, random_string


class NotionExporter:
    """
    Export a Jupyter notebook to Notion.

    Parameters
    ----------
    notion_api_key : str
        Notion API key.
    project_id : str, optional
        The project ID of the Google Cloud project. This is necessary to export media data to Google Drive.
        Notion API does not support media upload, so we need to upload media files to Google Drive
        and get the URL to embed. The default is "dsg-sandbox".
    notion_api_key_version : str, optional
        The version of the secret that stores the Notion API key.
        The default is "1".
    credential_path : str, optional
        The path to the service account key file.
        The default is None.
    scopes : list[str], optional
        The list of scopes to request.
        If None, the default scopes are
        "https://www.googleapis.com/auth/drive" and "https://www.googleapis.com/auth/cloud-platform".
        The default is None.
    logger : logging.Logger, optional
        The logger object.
        The default is None.

    Attributes
    ----------
    notion_client : notion_extension.Client
        The Notion client.
    drive_service : googleapiclient.discovery.Resource
        The Google Drive service.
    """

    def __init__(
        self,
        notion_api_key: str,
        project_id: str = "dsg-sandbox",
        credential_path: str | None = None,
        scopes: list[str] | None = None,
        logger: logging.Logger | None = None,
    ):
        if logger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

        self.scopes = scopes or [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
        ]

        if credential_path or project_id:
            if credential_path is None:
                credentials, _ = default(scopes=self.scopes, quota_project_id=project_id)
            else:
                credentials = ServiceAccountCredentials.from_service_account_file(
                    credential_path, scopes=self.scopes
                )

            self.drive_service = build("drive", "v3", credentials=credentials)
        else:
            self.drive_service = None

        self.notion_client = Client(auth=notion_api_key)

    def _to_notion_blocks(self, cells: list[Cell], drive_dir_id: str | None) -> list[Block]:
        blocks = []
        flag_warning = False
        for cell in cells:
            if cell.type == "output":
                mime_type = cell.mime_type
                if mime_type in {"image/jpeg", "image/png"}:
                    if drive_dir_id is None and not flag_warning:
                        self.logger.warning(
                            "drive_dir_id is not specified. Media data in the notebook will be ignored."
                        )
                        flag_warning = True

                    if self.drive_service is None and not flag_warning:
                        self.logger.warning(
                            "Google Drive API is not available. Media data in the notebook will be ignored."
                        )
                        flag_warning = True

                    if flag_warning:
                        continue

                    if cell.image is None:
                        raise ValueError("The image data is not found.")

                    image_bytes = pil2bytes(cell.image)

                    file_name = random_string() + f".{mime_type.split('/')[1]}"

                    file_metadata = {"name": file_name, "parents": [drive_dir_id]}

                    # Notion API dose not support media upload,
                    # so we need to upload the media file to Google Drive and get the URL to embed.
                    media = MediaIoBaseUpload(image_bytes, mimetype=mime_type, resumable=True)
                    request = self.drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        supportsAllDrives=True,
                    )
                    status, done = request.next_chunk()

                    file_url = f"https://lh3.googleusercontent.com/d/{done['id']}"

                    blocks.append(Block.embed(url=file_url))
                else:
                    blocks.append(
                        Block.code(content=cell.text, language="plain text", caption="output")
                    )

            elif cell.type == "markdown":
                if cell.text is None:
                    continue

                blocks.extend(Blocks.from_markdown(text=cell.text).blocks)

            elif cell.type == "code":
                if cell.mime_type == "text/markdown" and cell.text is not None:
                    # comments in the code cell are treated as markdown
                    blocks.extend(Blocks.from_markdown(text=cell.text.strip(" #")).blocks)

        return blocks

    def export(
        self,
        notebook_path: str | Path,
        db_properties: Properties,
        database_id: str,
        drive_dir_id: str | None = None,
    ) -> None:
        """
        Export a Jupyter notebook to Notion.

        Parameters
        ----------
        notebook_path : str or Path
            The path to the Jupyter notebook.
        db_properties : Properties
            The properties of the database.
        database_id : str
            The ID of the database.
        drive_dir_id : str, optional
            The ID of the Google Drive directory to store media files.
            The default is None. If None, media files in the notebook will be ignored.
        """
        cells = NotebookExtractor.extract(notebook_path=notebook_path)
        blocks = self._to_notion_blocks(cells=cells, drive_dir_id=drive_dir_id)

        # Notion API limits the number of blocks per request to 100.
        # See: https://developers.notion.com/reference/request-limits
        for i, batch in enumerate(make_batch(blocks, batch_size=1)):
            if i == 0:
                page = self.notion_client.create_page(
                    database_id=database_id,
                    properties=db_properties,
                    page_contents=Blocks(blocks=batch),
                )
            else:
                self.notion_client.append_blocks_to_page(
                    page_id=page["id"],
                    blocks=Blocks(blocks=batch),
                )
