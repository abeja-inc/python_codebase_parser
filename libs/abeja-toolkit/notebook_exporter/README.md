# Notebook-exporter

This tools is responsible for exporting jupyter notebook to specified location like notion database. Supported destination is: 

- Notion
    - notion integration used for this tool is `notebook-converter`.
    - `notebook-converter` is introduced into `DS Project Master DB` in default.
        - notion exporter can insert a page into the database under the `DS Project Master DB`, for example, `DS Note` database in each technical documents.
        - notion api key is managed on google cloud project `dsg-sandbox`.
    - If you are the member except DSG, and want to use this tool, please ask itsupport to create new notion integration and setting the notion api key to secret manager on other google cloud project. After that, please change the arguments value to fit your expectation when running (See: [Basic usage](#basic-usage)).

## Prerequisites

### Settings for google cloud and drive api

1. Set IAM role on Google Cloud to access secret manager

Notion API key is managed by the secret manager on Google Cloud. In default, the secret in `dsg-sandbox` project is used, so please make sure if you have the role to access secret manager; `Secret Manager Secret Accessor` in `dsg-sandbox` project.


2. [Optional] Decide drive folder to upload media data in the notebook and get the folder id

This tool treats media data like image or figure in the notebook as a embed block in the notion because Notion API does not support direct uploading of the media data. Media data is uploaded to Google Drive at first, and getting the URL, then that URL is embed to the notion page. This url is just reference url of the Drive, so permission scope follows the Drive setting. Uploaded media data has random name.

Currently supported media: 
- image displayed by `PIL.Image`
- figure displayed by `matplotlib.pyplot`

Drive folder id is included in the URL of the folder. Here is an example of the drive folder URL and display of where the folder id is.

`https://drive.google.com/drive/folders/<folder_id>?xxxxxxxxx`

After that, please activate drive api for your google cloud project.

3. Authenticate for google drive and google cloud

Please authenticate via google CLI as needed. Service account credential is also supported. If you want to authenticate via google CLI, run this command after installing google CLI.

```shell
# in the case where you don't need to export media data
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform

# If you want to export media data as well
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform
```

If you want to use service account, please give the service account permission.

4. [Optional] Set environmental variable

For command line function, the script loads environmental variables so it makes repeated export easy to set the environmental variables as shown below.

- `DRIVE_DIR_ID`: it's needed to export media data in the notebook.


### For exporting to notion

1. Connect integration with your database

For DSG members, notion integration `notebook-converter` is already introduced into `DS Project Master DB`, so nothing to do unless you want to export to database that isn't under the `DS Project Master DB`. For other group members, please other notion integration prepared by itsupport with your database.

2. Find notion database id

You can find database id in the URL. The database to store must be connected with `notebook-converter` integration. The URL is like this. 

`https://www.notion.so/abejainc/<database_id>?v=xxxxxxxxxxxx`

3. [Optional] Set environmental variable

- `NOTION_DATABASE_ID`: the id of the notion database you want to export to.

## Installation

This tool depends on the tool; `notion_extension`, so you have to checkout `notion_extension` package when you clone `abeja-toolkit`.

```shell
# for poetry
poetry add --editable /path/to/notebook_exporter

# for pip
pip install -e /path/to/notebook_exporter

```

## Basic usage

Exporter is used in the shell basically.

### For notion exporter

Here is an example of notion exporter's command. 

```shell
python /path/to/notion_exporter/export.py notion -nb </path/to/notebook/to/export> -db <notion_database_id> --title <page_title_in_the_notion_database> 
```

This exporter converts markdown cells and cell outputs to notion blocks and creates new notion page into specified database. Code cell is ignored. The cells under the markdown cell `# ToNotion` are the target of converting. For more detail, please see [the sample notebook](./example/sample_notebook.ipynb). 

Command options:
|options|description|required/optional|default|
|---|---|---|---|
|`-nb`|path to the notebook to export|required||
|`-db`|database id in the notion|required|env value of `NOTION_DATABASE_ID`|
|`-drive`|folder id of the google drive to store media data|optional|env value of `DRIVE_DIR_ID`|
|`--title`|page title in the notion database|optional|`""`|
|`--title_property_name`|title property name of the notion database|optional|`Task`|
|`--credential`|path to the credential file of the service account|optional|`None`|
|`--project_id`|project id of the google cloud|optional|`dsg-sandbox`|
|`--notion_api_key_name`|secret name of the notion api key on the secret manager|optional|`notion_notebook_converter`|
|`--notion_api_key_version`|the secret version on the secret manager|optional|`"1"`|
