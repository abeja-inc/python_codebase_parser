import json
from io import StringIO
from typing import Any

import gspread
import pandas as pd
from google.auth import default
from google.oauth2.service_account import Credentials
from gspread.auth import authorize
from gspread.spreadsheet import Spreadsheet
from gspread.utils import ValueInputOption
from gspread.worksheet import JSONResponse, ValueRange, Worksheet
from gspread_dataframe import set_with_dataframe


class SpreadSheet:
    """
    This class is a wrapper for gspread.Spreadsheet.

    Parameters
    ----------
    sheet_id : str
        The ID of the Google Sheet.
    quota_project_id : str, optional
        The project ID to use for the quota and billing, by default None.
    credential_path : str, optional
        The path to the service account credential file, by default None.
    scopes : list[str], optional
        The scopes of the Google API, by default None.
    """

    def __init__(
        self,
        sheet_id: str,
        quota_project_id: str | None = None,
        credential_path: str | None = None,
        scopes: list[str] | None = None,
    ):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        if credential_path is None:
            credentials, project_id = default(
                default_scopes=scopes, quota_project_id=quota_project_id
            )
        else:
            credentials = Credentials.from_service_account_file(credential_path, scopes=scopes)

        gc = authorize(credentials)
        self._sheet = gc.open_by_key(sheet_id)

    @property
    def sheet(self) -> Spreadsheet:
        """
        Get the Google Sheet object.

        Returns
        -------
        Spreadsheet
            The Google Sheet object.
        """
        return self._sheet

    def _get_sheet(self, worksheet_name: str) -> Worksheet:
        try:
            return self._sheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
        except gspread.exceptions.APIError:
            return self._sheet.worksheet(worksheet_name)

    def as_dataframe(self, worksheet_name: str) -> pd.DataFrame:
        """
        Get the worksheet as a pandas DataFrame.

        Parameters
        ----------
        worksheet_name : str
            The name of the worksheet.

        Returns
        -------
        pd.DataFrame
            The worksheet as a pandas DataFrame.
        """
        worksheet = self._get_sheet(worksheet_name)
        return pd.read_json(StringIO(json.dumps(worksheet.get_all_records())))

    def get(self, worksheet_name: str) -> ValueRange | list[list[Any]]:
        """
        Get the values of the worksheet.

        Parameters
        ----------
        worksheet_name : str
            The name of the worksheet.

        Returns
        -------
        ValueRange | list[list[Any]]
            The values of the worksheet.
        """
        worksheet = self._get_sheet(worksheet_name)
        return worksheet.get_all_values()

    def set_cols(self, worksheet_name: str, cols: list[str]) -> None:
        """
        Set the columns of the worksheet.

        Parameters
        ----------
        worksheet_name : str
            The name of the worksheet.
        cols : list[str]
            The columns to set.
        """
        worksheet = self._get_sheet(worksheet_name)
        col_range = f"A1:{chr(64+len(cols))}1"
        worksheet.update([cols], col_range)

    def _append(self, worksheet: Worksheet, row: list[Any]) -> JSONResponse:
        print("POST: ", row)
        return worksheet.append_row(row, value_input_option=ValueInputOption.user_entered)

    def append(self, worksheet_name: str, row: dict[str, Any]) -> JSONResponse:
        """
        Append a row to the worksheet.

        Parameters
        ----------
        worksheet_name : str
            The name of the worksheet.
        row : dict[str, Any]
            The row to append. The keys are the column names.

        Returns
        -------
        JSONResponse
            The response of the API.
        """
        worksheet = self._get_sheet(worksheet_name)

        keys = worksheet.row_values(1)
        row_to_append = []
        for key in keys:
            row_to_append.append(row[key] if key in row else "")
        return self._append(worksheet, row_to_append)

    def to_sheet(self, worksheet_name: str, df: pd.DataFrame) -> None:
        """
        Set the DataFrame to the worksheet.

        Parameters
        ----------
        worksheet_name : str
            The name of the worksheet.
        df : pd.DataFrame
            The DataFrame to set.
        """
        worksheet = self._get_sheet(worksheet_name)
        set_with_dataframe(worksheet, df)
