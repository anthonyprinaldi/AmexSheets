import datetime
import time
import webbrowser
from pathlib import Path
from typing import Optional

import pandas as pd

from amexsheets.consts import SAVE_DIR
from amexsheets.custom_enums import Month


class AmexData:
    BASE_URL = 'https://global.americanexpress.com/myca/intl/istatement/canlac/excel.do'
    REQUEST_URL = '?&method=createExcel&Face=en_CA&sorted_index=0&BPIndex=-1&requestType=searchDateRange&includeTransDetails=Yes'
    DATE_FORMAT = '%Y%m%d'
    DOWNLOAD_TIMEOUT = 20.0
    DOWNLOAD_POLL_INTERVAL = 1.0
    DEFAULT_FILE = Path.home() / 'Downloads' / 'Summary.xls'

    COLUMNS = ['Date', 'Description', 'Amount', 'Merchant']
    START_ROW = 11
    IGNORE_VALS = ['PAYMENT RECEIVED - THANK YOU']
    DATE_STRPTIME = '%d %b %Y'

    def __init__(self, start_date: datetime.datetime, end_date: datetime.datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_str = self._get_date_str(start_date)
        self.end_date_str = self._get_date_str(end_date)
        self.archive_file = SAVE_DIR / f'amex_{datetime.date.today().strftime(self.DATE_FORMAT)}.xls'
    
    def _get_date_str(self, date: datetime.datetime) -> str:
        return date.strftime(self.DATE_FORMAT)
    
    @property
    def _start_date_url(self) -> str:
        return f'&currentStartDate={self.start_date_str}'
    
    @property
    def _end_date_url(self) -> str:
        return f'&currentEndDate={self.end_date_str}'
    
    def _compose_url(self) -> str:
        return self.BASE_URL + self.REQUEST_URL + self._start_date_url + self._end_date_url
    
    def _move_existing_file(self):
        if self.DEFAULT_FILE.exists():
            self.DEFAULT_FILE.rename(self.DEFAULT_FILE.with_suffix('.old.xls'))
    
    def _archive_file(self):
        if self.DEFAULT_FILE.exists():
            self.archive_file.parent.mkdir(parents=True, exist_ok=True)
            self.DEFAULT_FILE.rename(self.archive_file)
    
    def _load_data(self) -> pd.DataFrame:
        df = pd.read_excel(self.archive_file, header=self.START_ROW)[self.COLUMNS]
        df['Date'] = pd.to_datetime(df['Date'], format=self.DATE_STRPTIME)
        df['Month'] = df['Date'].dt.month.apply(lambda x: Month.from_int(x))
        # df = df[df['Month'] == month]
        df = df[~df['Description'].isin(self.IGNORE_VALS)]
        df['Identifier'] = df['Merchant'] + '__' + df['Description']
        df['Details'] = ''
        df['Category'] = ''
        return df
    
    def download_and_load(self, filter_month: Optional[Month] = None) -> pd.DataFrame:
        self._move_existing_file()
        webbrowser.open(self._compose_url(), new=1)
        print(f'Downloading...')

        start_time = time.time()

        while time.time() - start_time < self.DOWNLOAD_TIMEOUT:
            if self.DEFAULT_FILE.exists():
                print(f'Download complete: {self.DEFAULT_FILE}')
                break
            time.sleep(self.DOWNLOAD_POLL_INTERVAL)
        
        time.sleep(1)
        
        if not self.DEFAULT_FILE.exists():
            raise TimeoutError(f'Download timed out after {self.DOWNLOAD_TIMEOUT} seconds')
        
        self._archive_file()

        df = self._load_data()
        return df[df['Month'] == filter_month] if filter_month else df


if __name__ == '__main__':
    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 1, 31)
    amex_data = AmexData(start_date, end_date)
    print(amex_data.download_and_load())