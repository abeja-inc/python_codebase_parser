# Spreadsheet

**NOTE: This tool is under developing.**

This tool is helper module to integrate your experimental pipeline and google spreadsheet, mainly focusing reading spreadsheet as a pandas dataframe and uploading a dataframe to spreadsheet.

## Installation

You can install this tool by `pip` or `poetry` after checkout of the code.

```shell
poetry add --editable /path/to/spreadsheet

# or

pip install -e /path/to/spreadsheet
```

## Prerequisites

There are 2 ways to authorize using service account or google cloud sdk.

### Using service account

1. Setup the google cloud project.
2. Create service account.
3. Invite service account to your spreadsheet.
4. Create credential json file of the service account, and locate in your environment.

After those steps, you can access to your spreadsheet via the service account.

```python
from spreadsheet import SpreadSheet

spreadsheet = SpreadSheet(
    sheet_id="<your sheet id>",
    credential_path="path/to/your/service-account/credential/file.json",
)
```


### Using google cloud sdk

If your IAM or role have sufficient permission, you can also authorize via google cloud sdk. For the steps to setup google cloud sdk, please see: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).

After setup google cloud sdk, please login with this command

```shell
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/spreadsheets
```

Now you can access your spreadsheet.

```python
from spreadsheet import SpreadSheet

spreadsheet = SpreadSheet(
    sheet_id="<your sheet id>", quota_project_id="<your project id>"
)
```

## Basic usage

### Get worksheet as a pandas dataframe

```python
spreadsheet.as_dataframe("<worksheet name to fetch>")
```

### Upload pandas dataframe to the spreadsheet

```python
spreadsheet.to_sheet(
    worksheet_name="<worksheet name to store>",
    df=df,
)
```

### Append a row to the spreadsheet

NOTE: `SpreadSheet.append()` method takes the first row values in the spreadsheet as the columns. 

```python
df = spreadsheet.as_dataframe("<worksheet name>")
cols = df.columns.to_list()

row = {col: "test" for col in cols}

spreadsheet.append("<worksheet name>", row)
```
