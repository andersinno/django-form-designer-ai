from django import template
from django.db.models.query import QuerySet
from django.template.defaultfilters import yesno
from django.utils.encoding import force_str

register = template.Library()

# Returns a more "human-friendly" representation of value than repr()


def friendly(value, null_value=None):
    if value is None and null_value is not None:
        return null_value
    if isinstance(value, (QuerySet, list)):
        value = ", ".join(force_str(object) for object in value)
    if isinstance(value, bool):
        value = yesno(value)
    if hasattr(value, "url"):
        value = value.url
    return force_str(value)



register.filter(friendly)
