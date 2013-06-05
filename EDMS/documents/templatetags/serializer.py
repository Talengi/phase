import json

from django import template
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.template.defaultfilters import safe


register = template.Library()

@register.filter
def jsonify(value):
    """return a json encoded version of the value"""
    return safe(serialize("json", value))
