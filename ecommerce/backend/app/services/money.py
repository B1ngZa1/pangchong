"""Money helpers for order pricing.

All arithmetic is performed in integer minor units.  Decimal values are only
used at the database/API boundary so binary floating-point never participates
in a transaction total.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


MoneyInput = Union[Decimal, int, str]
MINOR_UNIT = Decimal("0.01")
MINOR_UNITS_PER_MAJOR = 100


def as_decimal(value: MoneyInput) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def to_minor_units(value: MoneyInput) -> int:
    rounded = as_decimal(value).quantize(MINOR_UNIT, rounding=ROUND_HALF_UP)
    return int(rounded * MINOR_UNITS_PER_MAJOR)


def from_minor_units(value: int) -> Decimal:
    return (Decimal(value) / MINOR_UNITS_PER_MAJOR).quantize(MINOR_UNIT)
