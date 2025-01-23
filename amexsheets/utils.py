import re


def convert_dollar_to_float(amount: str) -> float:
    if isinstance(amount, str) and re.findall(r'(\$\d+(\.\d+)?)\b', amount):
        return float(re.sub(r'[^\d.-]', '', amount))
    return amount

def convert_amount_to_idetifier_str(amount: float) -> str:
    return str(amount).replace('.', 'P').replace('-', 'M')