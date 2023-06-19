import pytest
from django.forms.models import model_to_dict
from django.utils.crypto import get_random_string

from form_designer.models import FormDefinition


@pytest.mark.django_db
def test_admin_list_view_renders(admin_client, greeting_form):
    assert (
        greeting_form.name
        in admin_client.get("/admin/form_designer/formdefinition/").content.decode()
    )


@pytest.mark.django_db
def test_admin_create_view_renders_add(admin_client):
    assert admin_client.get("/admin/form_designer/formdefinition/add/").content


@pytest.mark.django_db
@pytest.mark.parametrize("n_fields", range(5))
def test_admin_create_view_creates_form(admin_client, n_fields):
    name = get_random_string(12)
    data = {
        "_save": "Save",
        "action": "",
        "allow_get_initial": "on",
        "body": "",
        "error_message": "",
        "form_template_name": "",
        "formdefinitionfield_set-INITIAL_FORMS": "0",
        "formdefinitionfield_set-MAX_NUM_FORMS": "1000",
        "formdefinitionfield_set-MIN_NUM_FORMS": "0",
        "formdefinitionfield_set-TOTAL_FORMS": n_fields,
        "log_data": "on",
        "mail_from": "",
        "mail_subject": "",
        "mail_to": "",
        "mail_uploaded_files": "on",
        "message_template": "",
        "method": "POST",
        "name": name,
        "save_uploaded_files": "on",
        "submit_label": "",
        "success_clear": "on",
        "success_message": "",
        "success_redirect": "on",
        "title": "",
    }

    for i in range(n_fields):
        data.update(
            {
                key.replace("NUM", str(i)): value
                for (key, value) in {
                    "formdefinitionfield_set-NUM-field_class": "django.forms.CharField",
                    "formdefinitionfield_set-NUM-include_result": "on",
                    "formdefinitionfield_set-NUM-label": "test %d" % i,
                    "formdefinitionfield_set-NUM-name": "test%d" % i,
                    "formdefinitionfield_set-NUM-position": i,
                    "formdefinitionfield_set-NUM-required": "on",
                }.items()
            }
        )

    admin_client.post("/admin/form_designer/formdefinition/add/", data=data)

    fd = FormDefinition.objects.get(name=name)
    assert fd.formdefinitionfield_set.count() == n_fields
    for key, value in model_to_dict(fd).items():  # Verify our posted data
        if key not in data:
            continue
        if value is True:
            assert data[key] == "on"
        else:
            if data[key] == "":
                assert data[key] == value or value is None
            else:
                assert data[key] == value


@pytest.mark.django_db
def test_admin_list_view_renders_formlog(admin_client, greeting_form_with_log):
    log = greeting_form_with_log.logs.first()
    greeting_value = log.data[0]["value"]
    assert (
        greeting_value
        in admin_client.get("/admin/form_designer/formlog/").content.decode()
    )


@pytest.mark.django_db
def test_admin_create_view_renders(admin_client, greeting_form_with_log):
    assert admin_client.get("/admin/form_designer/formlog/add/").content


@pytest.mark.django_db
@pytest.mark.parametrize("format", ("CSV", "XLS"))
def test_admin_export_view(admin_client, greeting_form_with_log, format):
    assert admin_client.get(f"/admin/form_designer/formlog/export/{format}/").content
