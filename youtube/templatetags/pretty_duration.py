import time

from django import template

register = template.Library()


@register.filter
def pretty_duration(value):
    time_value = time.gmtime(value)

    if time_value.tm_hour > 0:
        return time.strftime('%H:%M:%S', time_value)

    return time.strftime('%M:%S', time_value)
