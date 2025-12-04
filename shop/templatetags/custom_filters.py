from django import template

register = template.Library()

@register.filter
def format_price(value):
    """Format number with spaces as thousands separator"""
    if not value:
        return '0'
    try:
        # Convert to integer and format with spaces
        num = int(float(value))
        return str(num).replace('.', '').replace(',', '')[::-1]
    except (ValueError, TypeError):
        return value


@register.filter
def space_thousands(value):
    """Format number with spaces as thousands separator"""
    if value is None:
        return '0'
    try:
        # Convert to string and remove any existing separators
        num_str = str(int(float(str(value).replace(' ', '').replace(',', ''))))
        # Add spaces as thousands separator
        return '{:,}'.format(int(num_str)).replace(',', ' ')
    except (ValueError, TypeError):
        return value
