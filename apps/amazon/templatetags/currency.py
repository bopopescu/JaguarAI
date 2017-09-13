from django import template
from django.db.models import F
from django.utils.safestring import mark_safe

from apps.amazon.models import BrowseNode

register = template.Library()

TOP_LEVEL_BROWSE_NODES = [
    2350149011, 2617941011, 15684181, 165796011, 3760911,
    384082011, 283155, 502394, 2335753011, 468642, 541966,
    172282, 16310211, 3760901, 1055398, 16310161, 133140011,
    284507, 599858, 2625373011, 5174, 11091801, 1064954,
    2619533011, 229534, 3375251, 228013, 165793011,
]


@register.filter()
def subtract(value, second):
    second = second or 0
    return value - second


@register.filter()
def currency(value):
    value = value or 0
    if isinstance(value, str):
        value = float(value)
    return f"${value:,.2f}"


@register.simple_tag
def global_nodes(*args):
    nodes = BrowseNode.objects.filter(
        id=F('top_level_node'), id__in=TOP_LEVEL_BROWSE_NODES
    ).order_by('name')
    return mark_safe(
        "<option></option>" + "".join(
            f"<option value='{node.id}'>{node.name}</option>" for node in nodes
        ))
