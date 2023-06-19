import pytest

from form_designer.forms import DesignedForm


@pytest.mark.django_db
def test_custom_message_template(greeting_form):
    """
    Test that custom message templates work as expected.
    """
    greeting_form.message_template = "{{ greeting }}, friend!"
    form = DesignedForm(
        greeting_form,
        data={
            "greeting": "Hello",
        },
    )
    assert form.is_valid()
    greeting_form.log(form)
    mail = greeting_form.send_mail(form)
    assert mail.body == "Hello, friend!"
