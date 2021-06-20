from django.db import models

from cms.models import CMSPlugin
from form_designer.models import FormDefinition\

from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

class CMSFormDefinition(CMSPlugin):
    form_definition = models.ForeignKey(FormDefinition, verbose_name=_('form'), on_delete=models.CASCADE)

    def __str__(self):
        return force_str(self.form_definition)
