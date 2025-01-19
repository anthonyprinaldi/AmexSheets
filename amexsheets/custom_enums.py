import enum

class ListEnum(enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: cls(c.value), cls))
    
    def __str__(self) -> str:
        return self.value


class Month(str, ListEnum):
    JAN = 'JAN'
    FEB = 'FEB'
    MAR = 'MAR'
    APR = 'APR'
    MAY = 'MAY'
    JUN = 'JUN'
    JUL = 'JUL'
    AUG = 'AUG'
    SEP = 'SEP'
    OCT = 'OCT'
    NOV = 'NOV'
    DEC = 'DEC'

    @staticmethod
    def from_int(month: int) -> 'Month':
        return Month.list()[month - 1]
    
    def to_int(self) -> int:
        return Month.list().index(self) + 1

class Sheet(str, ListEnum):
    PERSONAL_MONTHLY_BUDGET_2025 = 'PERSONAL MONTHLY BUDGET 2025'