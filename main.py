import datetime

import pydantic_argparse

from amexsheets.amex_data import AmexData
from amexsheets.arguments import Arguments
from amexsheets.consts import PROG
from amexsheets.custom_enums import Month
from amexsheets.gsheets_data import GSheetsData
from utils import read


def main():

    parser = pydantic_argparse.ArgumentParser(
        model=Arguments,
        prog=PROG,
        description='Download and update Amex transactions to Google Sheets',
        version=read(PROG, 'VERSION'),
    )
    args = parser.parse_typed_args()

    amex = AmexData(
        start_date=args.start_date,
        end_date=args.end_date,
    )
    g = GSheetsData(
        month=args.month,
        amex_df=amex.download_and_load(filter_month=args.month),
    )
    g.run_update()
    print('Done')



if __name__ == '__main__':
    main()