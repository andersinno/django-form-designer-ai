from distutils.version import StrictVersion as Ver

from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.utils.crypto import get_random_string

import pytest

try:
    import cms
    from cms import api
    from cms.models import Page, Placeholder
    from form_designer.contrib.cms_plugins.form_designer_form.cms_plugins import FormDesignerPlugin
    from form_designer.contrib.cms_plugins.form_designer_form.models import CMSFormDefinition
    from form_designer.models import FormDefinition, FormDefinitionField
    CMS_VERSION = Ver(cms.__version__)

except ImportError:
    pytestmark = pytest.mark.skip('django-cms not importable')



@pytest.mark.django_db
def test_cms_plugin_renders_in_cms_page(rf):
    fd = FormDefinition.objects.create(
        mail_to='test@example.com',
        mail_subject='Someone sent you a greeting: {{ test }}'
    )
    field = FormDefinitionField.objects.create(
        form_definition=fd,
        name='test',
        label=get_random_string(12),
        field_class='django.forms.CharField',
    )
    page = api.create_page("test", "page.html", "en")
    assert isinstance(page, Page)
    ph = page.get_placeholders()[0]
    assert isinstance(ph, Placeholder)
    plugin = api.add_plugin(ph, FormDesignerPlugin, "en", form_definition=fd)
    assert isinstance(plugin, CMSFormDefinition)
    assert plugin.form_definition == fd
    request = rf.get("/")
    request.user = AnonymousUser()
    request.current_page = page
    if CMS_VERSION >= Ver('3.4'):
        from cms.plugin_rendering import ContentRenderer
        renderer = ContentRenderer(request)
        context = RequestContext(request)
        context['request'] = request
        content = renderer.render_plugin(plugin, context)
    else:
        from cms.page_rendering import render_page
        response = render_page(request, page, "fi", "test")
        response.render()
        content = response.content.decode("utf8")
    assert field.label in content
    assert "<form" in content
