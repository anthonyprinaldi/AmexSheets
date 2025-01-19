import datetime
import pydantic

from amexsheets.custom_enums import Month


class Arguments(pydantic.BaseModel):
    # Required Args
    month: Month = pydantic.Field(description='Month to download and update')

    start_date: datetime.datetime = None
    end_date: datetime.datetime = None

    @pydantic.root_validator(pre=False)
    def __post_init__(cls, values):
        """
        Gets the start and end datetime object for the month
        based on the month enum
        """
        month = values.get('month')
        if not month:
            raise ValueError('Month is required')
        
        values['start_date'] = datetime.datetime(
            datetime.date.today().year,
            month.to_int(),
            1,
        )
        values['end_date'] = datetime.datetime(
            datetime.date.today().year,
            month.to_int() + 1 % 12,
            1,
        ) - datetime.timedelta(days=1)

        return values