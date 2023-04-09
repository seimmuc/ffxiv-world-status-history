from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(trim_blocks=True, lstrip_blocks=True, **options)
    env.globals.update({
        'static': static,
        'url': reverse
    })
    return env
