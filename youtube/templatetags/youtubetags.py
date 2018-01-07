import datetime

from dateutil.relativedelta import relativedelta
from django import template
from django.utils import timezone
from django.utils.html import format_html

from ..models import Channel

register = template.Library()


@register.simple_tag
def visible_channels():
    return Channel.objects.filter(hidden=False).order_by('title')


@register.simple_tag
def hidden_channels():
    return Channel.objects.filter(hidden=True).order_by('title')


@register.filter
def timesince_short(fromdate):
    if not isinstance(fromdate, (datetime.date, datetime.datetime)):
        raise TypeError("fromdate should be a datetime type.")

    delta = relativedelta(timezone.now(), fromdate)
    if delta.years > 0:
        return format_html('{}y{}m ago', delta.years, delta.months)
    elif delta.months > 0:
        return format_html('{}m{}D ago', delta.months, delta.days)
    elif delta.days > 0:
        return format_html('{}D{}h ago', delta.days, delta.hours)
    else:
        return format_html('{}h{}m ago', delta.hours, delta.minutes)
