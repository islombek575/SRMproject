from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

CENTS = Decimal("0.01")

def to_decimal(value, default=Decimal("0.00")):
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value.quantize(CENTS, rounding=ROUND_HALF_UP)
    try:
        return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return default

def ensure_positive(value):
    d = to_decimal(value)
    if d < 0:
        raise ValueError("Value must be positive")
    return d

def safe_subtract(a, b):
    return to_decimal(a) - to_decimal(b)
