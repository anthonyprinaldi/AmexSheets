from pathlib import Path
import string
import gspread
import gspread.utils
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

from amexsheets.custom_enums import Month, Sheet
from amexsheets.utils import convert_dollar_to_float


class GSheetsData:
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    TOKEN_LOCATION = Path(__file__).parent.parent / 'token.json'
    EXPENSE_START_ROW = 3
    AMOUNT_COL = 'M'
    CATEGORY_COL = 'N'
    DETAILS_COL = 'O'
    IDENTIFIER_COL = 'P'
    COLUMN_LETTERS = [
        AMOUNT_COL,
        CATEGORY_COL,
        DETAILS_COL,
        IDENTIFIER_COL,
    ]
    AMOUNT = 'Amount'
    CATEGORY = 'Category'
    DETAILS = 'Details'
    IDENTIFIER = 'Identifier'
    COLUMNS = [
        AMOUNT,
        CATEGORY,
        DETAILS,
        IDENTIFIER,
    ]

    FILE_NAME = Sheet.PERSONAL_MONTHLY_BUDGET_2025

    def __init__(self, month: Month, amex_df: pd.DataFrame):
        self._create_client()
        self.month = month
        self.amex_df = amex_df
    
    def _create_client(self):
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.TOKEN_LOCATION, self.SCOPE)
        self.client = gspread.authorize(self.creds)

    def _load_sheet(self):
        sheet = self.client.open(self.FILE_NAME)
        all_sheets = sheet.worksheets()
        sheet = [x for x in all_sheets if x.title == self.month]
        if not sheet:
            raise ValueError(f"Sheet {self.month} not found in {self.FILE_NAME}")
        
        self.sheet = sheet[0]
    
    def _get_existing_transactions(self):
        data = self.sheet.get_all_values()
        df = pd.DataFrame(data[self.EXPENSE_START_ROW+1:], columns=data[self.EXPENSE_START_ROW])
        col_index = list(map(lambda x: string.ascii_uppercase.index(x), self.COLUMN_LETTERS))
        df = df.iloc[:, col_index]
        self.df = df[~df.apply(lambda x: x.str.strip().eq(''), axis=0).all(axis=1)]
    
    def _get_new_transactions(self):
        self.new_transactions = self.amex_df[~self.amex_df['Identifier'].isin(self.df['Identifier'])]

    def _create_upload_df(self):
        new_transactions = self.new_transactions.sort_values(by='Date', ascending=False)
        transactions = pd.concat([
            new_transactions[self.COLUMNS],
            self.df,
        ])
        transactions[self.AMOUNT] = transactions[self.AMOUNT].apply(lambda x: str(convert_dollar_to_float(x)))
        transactions[self.AMOUNT] = transactions[self.AMOUNT].astype(float)
        self.df = transactions
    
    def _upload_transactions(self):
        range_name = f'{self.AMOUNT_COL}{self.EXPENSE_START_ROW+2}:{self.IDENTIFIER_COL}{self.EXPENSE_START_ROW+2+self.df.shape[0]}'
        self.sheet.update(
            self.df.values.tolist(),
            range_name=range_name,
        )
    
    def _add_data_validation(self):
        grid_range = gspread.utils.a1_range_to_grid_range(
            f'{self.CATEGORY_COL}{self.EXPENSE_START_ROW+2}:{self.CATEGORY_COL}{self.EXPENSE_START_ROW+1+self.df.shape[0]}',
        )
        sheet_id = self.sheet.id
        grid_range['sheetId'] = sheet_id
        reqs = [
            {
                'setDataValidation': {
                    'range': grid_range,
                    'rule': {
                        'strict': True,
                        'showCustomUi': True,
                        'condition': {
                            'type': 'ONE_OF_RANGE',
                            'values': [{'userEnteredValue': f"='Expense Categories'!$A$1:$A$41"}],
                        },
                    }
                }
            }
        ]
        self.sheet.spreadsheet.batch_update({'requests': reqs})
    
    def run_update(self):
        self._load_sheet()
        self._get_existing_transactions()
        self._get_new_transactions()
        self._create_upload_df()
        self._upload_transactions()
        self._add_data_validation()