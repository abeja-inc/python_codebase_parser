import os
from argparse import ArgumentParser


def main() -> None:
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest="to")
    notion_exporter_parser = subparser.add_parser("notion")

    # Notion Exporter
    notion_exporter_parser.add_argument(
        "-nb", "--notebook_path", type=str, required=True, help="Path to the notebook"
    )
    notion_exporter_parser.add_argument(
        "-db",
        "--database_id",
        type=str,
        default=os.getenv("NOTION_DATABASE_ID"),
        help="Notion Database ID",
    )
    notion_exporter_parser.add_argument("--title", type=str, default="", help="Title of the page")
    notion_exporter_parser.add_argument(
        "-drive",
        "--drive_dir_id",
        type=str,
        default=os.getenv("DRIVE_DIR_ID"),
        help="Google Drive Directory ID",
    )
    notion_exporter_parser.add_argument(
        "--title_property_name",
        type=str,
        default="Task",
        help="Title property name of the notion database",
    )
    notion_exporter_parser.add_argument(
        "--credential", type=str, default=None, help="Credential path for the service account"
    )
    notion_exporter_parser.add_argument(
        "--project_id", type=str, default="dsg-sandbox", help="Project ID of the google cloud"
    )
    notion_exporter_parser.add_argument(
        "--notion_api_key_name",
        type=str,
        default="notion_notebook_converter",
        help="Name of the API key which is managed by the secret manager on the google cloud",
    )
    notion_exporter_parser.add_argument(
        "--notion_api_key_version", type=str, default="1", help="Version of the API key"
    )

    args = parser.parse_args()

    if args.to == "notion":
        from notebook_exporter.notion import NotionExporter
        from notebook_exporter.secret import get_secret_on_google_cloud
        from notion_extension import Properties, Property

        notion_api_key = get_secret_on_google_cloud(
            project_id=args.project_id,
            secret_name=args.notion_api_key_name,
            secret_ver=args.notion_api_key_version,
        )

        exporter = NotionExporter(
            notion_api_key=notion_api_key,
            project_id=args.project_id,
            credential_path=args.credential,
        )

        exporter.export(
            notebook_path=args.notebook_path,
            db_properties=Properties(
                properties=[
                    Property.title(name=args.title_property_name, text=args.title),
                ]
            ),
            database_id=args.database_id,
            drive_dir_id=args.drive_dir_id,
        )
    else:
        raise ValueError(f"Unknown target: {args.to}")


if __name__ == "__main__":
    main()
