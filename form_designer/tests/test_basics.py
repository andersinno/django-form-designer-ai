from base64 import b64decode

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.base import BaseStorage
from django.core import mail
from django.core.files.base import ContentFile, File
from django.utils.crypto import get_random_string

from form_designer import settings as fd_settings
from form_designer.contrib.exporters.csv_exporter import CsvExporter
from form_designer.contrib.exporters.xls_exporter import XlsExporter
from form_designer.forms import DesignedForm
from form_designer.models import FormLog, FormValue
from form_designer.views import process_form

# https://raw.githubusercontent.com/mathiasbynens/small/master/jpeg.jpg

VERY_SMALL_JPEG = b64decode(
    "/9j/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgK"
    "CgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/"
    "yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k="
)


class OverriddenDesignedForm(DesignedForm):
    def clean_greeting(self):
        return self.cleaned_data["greeting"].upper()


@pytest.mark.django_db
@pytest.mark.parametrize("push_messages", (False, True))
@pytest.mark.parametrize("valid_data", (False, True))
@pytest.mark.parametrize("method", ("GET", "POST"))
@pytest.mark.parametrize("anon", (False, True))
@pytest.mark.parametrize("override_form", (False, "settings", "kwarg"))
def test_simple_form(
    monkeypatch,
    rf,
    admin_user,
    greeting_form,
    push_messages,
    valid_data,
    method,
    anon,
    override_form,
):
    fd = greeting_form
    message = f"zzz-å{get_random_string(12)}Ö"
    data = {
        "greeting": message,
        "upload": ContentFile(VERY_SMALL_JPEG, name="hello.jpg"),
        fd.submit_flag_name: "true",
    }
    if not valid_data:
        data.pop("greeting")

    if method == "POST":
        request = rf.post("/", data)
    elif method == "GET":
        data.pop("upload")  # can't upload via GET
        request = rf.get("/", data)

    request.user = AnonymousUser() if anon else admin_user
    request._messages = BaseStorage(request)
    kwargs = dict(
        push_messages=push_messages,
        disable_redirection=True,
    )
    if override_form == "kwarg":
        kwargs["form_class"] = OverriddenDesignedForm
    elif override_form == "settings":
        # Can't use the pytest-django settings fixture, since `form_designer.settings`
        # has non-lazy copies of Django settings taken at that module's import time.
        monkeypatch.setattr(
            fd_settings,
            "DESIGNED_FORM_CLASS",
            "form_designer.tests.test_basics.OverriddenDesignedForm",
        )

    context = process_form(request, fd, **kwargs)
    assert context["form_success"] == valid_data

    # Test that a message was (or was not) pushed
    assert len(request._messages._queued_messages) == int(push_messages)

    if valid_data:
        if (
            override_form
        ):  # If we've overridden the form, we expect an uppercase message
            message = message.upper()

        # Test that the form log was saved:
        flog = FormLog.objects.get(form_definition=fd)
        assert flog == context["form_log"]  # (and it's the same object in the context)
        name_to_value = {d["name"]: d["value"] for d in flog.data}
        assert name_to_value["greeting"] == message
        if name_to_value.get("upload"):
            assert isinstance(name_to_value["upload"], File)
        if not anon:
            assert flog.created_by == admin_user

        # Test that the email was sent:
        sent_email = mail.outbox[-1]

        assert (
            message in sent_email.subject
        )  # (since we customized the subject with a template)
        assert "greetingbot" in sent_email.message().get(
            "Reply-To"
        )  # (since we customized the reply-to address)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "exporter",
    [
        CsvExporter,
        XlsExporter,
    ],
)
@pytest.mark.parametrize("n_logs", range(5))
def test_export(rf, greeting_form, exporter, n_logs):
    if exporter is XlsExporter:
        pytest.importorskip("xlsx")
    message = "Térve"
    for n in range(n_logs):
        fl = FormLog.objects.create(form_definition=greeting_form)
        FormValue.objects.create(
            form_log=fl,
            field_name="greeting",
            value="%s %d" % (message, n + 1),
        )

    resp = exporter(greeting_form).export(
        request=rf.get("/"),
        queryset=FormLog.objects.filter(form_definition=greeting_form),
    )
    if "csv" in resp["content-type"]:
        # TODO: Improve CSV test?
        csv_data = resp.content.decode("utf8").splitlines()
        if n_logs > 0:  # The file will be empty if no logs exist
            assert csv_data[0].startswith("Created")
            assert "Greeting" in csv_data[0]
            for i in range(1, n_logs):
                assert message in csv_data[i]
                assert (f"{i}") in csv_data[i]
