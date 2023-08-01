from cms.models import CMSPlugin
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from form_designer.models import FormDefinition


class CMSFormDefinition(CMSPlugin):
    form_definition = models.ForeignKey(
        FormDefinition, verbose_name=_("form"), on_delete=models.CASCADE
    )

    def __str__(self):
        return force_str(self.form_definition)
