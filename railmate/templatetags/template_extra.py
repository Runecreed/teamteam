from django import template
from django.utils import dateparse
from datetime import date, datetime, time

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


@register.filter
def dateOnly(value):
    return value[0:10]


@register.filter
def timeOnly(value):
    return value[11:16]