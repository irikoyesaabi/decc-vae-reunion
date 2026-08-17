from django import template

register = template.Library()


@register.filter
def volet_label(point):
    return point.get_volet_label()
