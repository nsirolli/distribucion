from django import template
from django.template.defaultfilters import stringfilter

from materias.models import CargoDedicacion

register = template.Library()

@register.filter(name='restantes_hasta')
def restantes_hasta(it, cantidad):
    return range(len(it), cantidad)

@register.filter
@stringfilter
def cargo_nombre_largo(cargo_dedicacion):
    cd = CargoDedicacion[cargo_dedicacion]
    return cd.value