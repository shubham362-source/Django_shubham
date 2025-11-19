from django import template

register = template.Library()

@register.filter
def add(value, arg):
    """Add two values together."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value
