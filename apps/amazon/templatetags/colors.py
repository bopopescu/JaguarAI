from colour import Color
from django import template


register = template.Library()

# Set up the color gradient
_GREEN = Color(web="#66BB6A")
_WHITE = Color(web="#FFFFFF")
_RED = Color(web="#EF5350")
COLORS = list(_RED.range_to(_WHITE, 50)) + list(_WHITE.range_to(_GREEN, 50))


def green_white_red(value, arg) -> str:
    """Takes in the value and returns a web color."""
    # Validate the input
    if value is None:
        return _RED.get_web()
    value = float(value)
    args = [float(v) for v in arg.split(',')]
    if not len(args) == 2:
        raise ValueError("Must have 2 arguments in green_white_red!")
    first, last = args

    # Are we going backwards?
    inverse = first > last

    # What percentile are we in?
    d = value - last
    w = first - last
    percentile = int(d/w * 100)
    percentile = min(max(percentile, 0), 99)
    return COLORS[percentile].get_web()
register.filter('green_white_red', green_white_red)
