import time

from django import template

register = template.Library()


@register.filter
def pretty_duration(value):
    return time.strftime('%M:%S', time.gmtime(value))
