from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def currency(value):
    try:
        if isinstance(value, str):
            value = Decimal(value)
        return f'₹{value:,.2f}'
    except (ValueError, TypeError):
        return value