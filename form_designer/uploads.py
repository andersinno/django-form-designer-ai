import os
from types import SimpleNamespace

from django.core.files.base import File
from django.db.models.fields.files import FieldFile
from django.forms.forms import NON_FIELD_ERRORS
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from form_designer import settings as app_settings
from form_designer.utils import get_random_hash


def get_storage():
    if app_settings.FILE_STORAGE_NAME:  # Django 4.2+
        from django.core.files.storage import storages
        return storages[app_settings.FILE_STORAGE_NAME]
    if app_settings.FILE_STORAGE_CLASS:
        from django.core.files.storage import get_storage_class
        return get_storage_class(app_settings.FILE_STORAGE_CLASS)()
    from django.core.files.storage import default_storage
    return default_storage


def clean_files(form):
    total_upload_size = 0
    for field in form.file_fields:
        uploaded_file = form.cleaned_data.get(field.name, None)
        msg = None
        if uploaded_file is None:
            if field.required:
                msg = _("This field is required.")
            else:
                continue
        else:
            file_size = uploaded_file.size
            total_upload_size += file_size
            if (
                os.path.splitext(uploaded_file.name)[1].lstrip(".").lower() not in app_settings.ALLOWED_FILE_TYPES
            ):
                msg = _("This file type is not allowed.")
            elif file_size > app_settings.MAX_UPLOAD_SIZE:
                msg = _(
                    "Please keep file size under %(max_size)s. Current size is %(size)s."
                ) % {
                    "max_size": filesizeformat(app_settings.MAX_UPLOAD_SIZE),
                    "size": filesizeformat(file_size),
                }
        if msg:
            form._errors[field.name] = form.error_class([msg])

    if total_upload_size > app_settings.MAX_UPLOAD_TOTAL_SIZE:
        msg = _(
            "Please keep total file size under %(max)s. Current total size is %(current)s."
        ) % {
            "max": filesizeformat(app_settings.MAX_UPLOAD_TOTAL_SIZE),
            "current": filesizeformat(total_upload_size),
        }

        if NON_FIELD_ERRORS in form._errors:
            form._errors[NON_FIELD_ERRORS].append(msg)
        else:
            form._errors[NON_FIELD_ERRORS] = form.error_class([msg])

    return form.cleaned_data


def handle_uploaded_files(form_definition, form):
    files = []
    if form_definition.save_uploaded_files and len(form.file_fields):
        storage = get_storage()
        secret_hash = get_random_hash(10)
        for field in form.file_fields:
            uploaded_file = form.cleaned_data.get(field.name, None)
            if uploaded_file is None:
                continue
            valid_file_name = storage.get_valid_name(uploaded_file.name)
            root, ext = os.path.splitext(valid_file_name)
            filename = storage.get_available_name(
                os.path.join(
                    app_settings.FILE_STORAGE_DIR,
                    form_definition.name,
                    f"{root}_{secret_hash}{ext}",
                )
            )
            storage.save(filename, uploaded_file)
            form.cleaned_data[field.name] = StoredUploadedFile(name=filename)
            files.append(storage.path(filename))
    return files


class StoredUploadedFile(FieldFile):
    """
    A wrapper for uploaded files that is compatible to the FieldFile class, i.e.
    you can use instances of this class in templates just like you use the value
    of FileFields (e.g. `{{ my_file.url }}`)
    """

    def __init__(self, name):
        File.__init__(self, None, name)
        self.field = SimpleNamespace(storage=get_storage())
        self.instance = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Static files are read-only")  # pragma: no cover

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Static files are read-only")  # pragma: no cover

    def __str__(self):
        return self.name
