from decimal import Decimal
from datetime import datetime

def format_percentage(value: Decimal, decimals: int = 0) -> str:
    """Convierte un valor decimal (0.15) en porcentaje ('15%')"""
    percent = round(value * 100, decimals)
    return f"{percent:.{decimals}f}%"

def format_currency(value: float, symbol: str = "$") -> str:
    """Formatea un valor monetario"""
    return f"{symbol}{value:,.2f}"

def is_valid_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False

def get_discount_range(discount: float) -> str:
    """Devuelve una etiqueta de rango para un valor de descuento decimal"""
    if discount == 0:
        return "0%"
    elif discount <= 0.05:
        return "1% - 5%"
    elif discount <= 0.10:
        return "6% - 10%"
    elif discount <= 0.15:
        return "11% - 15%"
    elif discount <= 0.20:
        return "16% - 20%"
    else:
        return "> 20%"

def full_name(first: str, last: str, middle: Optional[str] = "") -> str:
    """Concatena nombre completo de forma segura"""
    parts = [first.strip()]
    if middle:
        parts.append(middle.strip())
    parts.append(last.strip())
    return " ".join(parts)