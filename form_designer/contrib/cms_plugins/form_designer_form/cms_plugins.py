
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from form_designer import settings
from form_designer.contrib.cms_plugins.form_designer_form.models import CMSFormDefinition
from form_designer.views import process_form


class FormDesignerPlugin(CMSPluginBase):
    model = CMSFormDefinition
    module = _('Form Designer')
    name = _('Form')
    admin_preview = False
    render_template = False
    cache = False  # New in version 3.0. see http://django-cms.readthedocs.org/en/latest/advanced/caching.html

    def render(self, context, instance, placeholder):
        if instance.form_definition.form_template_name:
            self.render_template = instance.form_definition.form_template_name
        else:
            self.render_template = settings.DEFAULT_FORM_TEMPLATE

        # Redirection does not work with CMS plugin, hence disable:
        return process_form(context['request'], instance.form_definition, context, disable_redirection=True,
                            push_messages=settings.PUSH_MESSAGES)


plugin_pool.register_plugin(FormDesignerPlugin)
