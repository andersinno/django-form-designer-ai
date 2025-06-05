from django.db.models import Count
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from form_designer import settings
from form_designer.templatetags.friendly import friendly


class ExporterBase:
    def __init__(self, model):
        self.model = model

    @staticmethod
    def is_enabled():
        return True

    @staticmethod
    def export_format():
        raise NotImplementedError()  # pragma: no cover

    def init_writer(self):
        raise NotImplementedError()  # pragma: no cover

    def init_response(self):
        raise NotImplementedError()  # pragma: no cover

    def writerow(self, row):
        raise NotImplementedError()  # pragma: no cover

    def close(self):
        pass

    @classmethod
    def export_view(cls, modeladmin, request, queryset):
        return cls(modeladmin.model).export(request, queryset)

    def export(self, request, queryset=None):
        raise NotImplementedError()  # pragma: no cover


class FormLogExporterBase(ExporterBase):
    def export(self, request, queryset=None):  # noqa: C901
        self.init_response()
        self.init_writer()
        distinct_forms = queryset.aggregate(Count("form_definition", distinct=True))[
            "form_definition__count"
        ]

        include_created = settings.CSV_EXPORT_INCLUDE_CREATED
        include_pk = settings.CSV_EXPORT_INCLUDE_PK
        include_header = settings.CSV_EXPORT_INCLUDE_HEADER and distinct_forms == 1
        include_form = settings.CSV_EXPORT_INCLUDE_FORM and distinct_forms > 1

        if queryset.count():
            fields = queryset[0].form_definition.get_field_dict()
            field_order = list(fields.keys())
            if include_header:
                header = []
                if include_form:
                    header.append(_("Form"))
                if include_created:
                    header.append(_("Created"))
                if include_pk:
                    header.append(_("ID"))
                # Form fields might have been changed and not match
                # existing form logs anymore.
                # Hence, use current form definition for header.
                # for field in queryset[0].data:
                #    header.append(field['label'] if field['label'] else field['key'])
                for field_name, field in fields.items():
                    header.append(field.label or field.name)

                self.writerow(
                    [
                        force_str(cell, encoding=settings.CSV_EXPORT_ENCODING)
                        for cell in header
                    ]
                )

            for entry in queryset:
                row = []
                if include_form:
                    row.append(entry.form_definition)
                if include_created:
                    row.append(entry.created)
                if include_pk:
                    row.append(entry.pk)
                name_to_value = {d["name"]: d["value"] for d in entry.data}
                for field in field_order:
                    value = friendly(
                        name_to_value.get(field),
                        null_value=settings.CSV_EXPORT_NULL_VALUE,
                    )
                    value = force_str(value, encoding=settings.CSV_EXPORT_ENCODING)
                    row.append(value)

                self.writerow(row)

        self.close()
        return self.response
