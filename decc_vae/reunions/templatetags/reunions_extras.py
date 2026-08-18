from django import template

from reunions.models import Parametre

register = template.Library()


@register.simple_tag
def get_logo():
    try:
        instance = Parametre.get_instance()
        if instance.logo and instance.logo_actif:
            return instance.logo.url
    except Exception:
        pass
    return None


@register.simple_tag
def get_app_name():
    try:
        return Parametre.get_instance().nom_application
    except Exception:
        return "DECC/VAE"
