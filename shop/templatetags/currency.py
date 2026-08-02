# shop/templatetags/currency.py
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def currency(value):
    """Format value as Indian Rupees"""
    if value is None:
        return ''
    
    try:
        # Convert to float
        amount = float(value)
        
        # Format with 2 decimal places and commas
        # For Indian format: 1,00,000.00
        formatted = f"{amount:,.2f}"
        
        # Return with Rupee symbol
        return f"₹{formatted}"
    except (ValueError, TypeError):
        return value

@register.filter
def currency_short(value):
    """Format value as Indian Rupees in short form (Lakh, Crore)"""
    if value is None:
        return ''
    
    try:
        amount = float(value)
        
        if amount >= 10000000:  # 1 Crore
            return f"₹{amount/10000000:.1f} Cr"
        elif amount >= 100000:  # 1 Lakh
            return f"₹{amount/100000:.1f} L"
        else:
            return f"₹{amount:,.0f}"
    except (ValueError, TypeError):
        return value

@register.filter
def inr_format(value):
    """Indian style number formatting"""
    if value is None:
        return ''
    
    try:
        amount = int(float(value))
        
        # Convert to string and reverse for Indian formatting
        s = str(amount)[::-1]
        # Group by 3, then 2, then 2...
        groups = [s[i:i+3] for i in range(0, len(s), 3)]
        # Reverse back
        result = ','.join(groups)[::-1]
        
        return f"₹{result}"
    except (ValueError, TypeError):
        return value