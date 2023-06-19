import pytest
from django.utils.crypto import get_random_string

from form_designer.models import FormLog


@pytest.fixture()
def greeting_form():
    from form_designer.models import FormDefinition, FormDefinitionField

    fd = FormDefinition.objects.create(
        name=get_random_string(12),
        mail_to="test@example.com",
        mail_subject="Someone sent you a greeting: {{ greeting }}",
        mail_reply_to="Greeting Bot <greetingbot@example.com>",
    )
    FormDefinitionField.objects.create(
        form_definition=fd,
        name="greeting",
        label="Greeting",
        field_class="django.forms.CharField",
        required=True,
    )
    FormDefinitionField.objects.create(
        form_definition=fd,
        name="upload",
        field_class="django.forms.FileField",
        required=False,
    )
    return fd


@pytest.fixture()
def greeting_form_with_log(admin_user, greeting_form):
    log = FormLog.objects.create(
        form_definition=greeting_form,
        created_by=admin_user,
    )
    log.values.create(field_name="greeting", value=get_random_string(12))
    return greeting_form
