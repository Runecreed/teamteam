from django import template

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def isDict(value):
    if isinstance(value, dict):
        return True
    else:
        return False
