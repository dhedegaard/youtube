from django import template

from ..models import Channel

register = template.Library()


@register.assignment_tag
def visible_channels():
    return Channel.objects.filter(hidden=False).order_by('title')
