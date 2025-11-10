from decimal import Decimal, ROUND_HALF_UP

CENTS = Decimal('0.01')
def to_decimal(v):
    if v is None:
        return Decimal('0.00')
    return (Decimal(str(v))).quantize(CENTS, rounding=ROUND_HALF_UP)


def ensure_positive(value):
    d = to_decimal(value)
    if d < 0:
        raise ValueError("Value must be positive")
    return d

def safe_subtract(a, b):
    return to_decimal(a) - to_decimal(b)
