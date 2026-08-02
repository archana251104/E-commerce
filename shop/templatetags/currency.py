# shop/templatetags/currency.py
from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format value as Indian Rupees"""
    if value is None:
        return ''
    
    try:
        amount = float(value)
        formatted = f"{amount:,.2f}"
        return f"₹{formatted}"
    except (ValueError, TypeError):
        return value