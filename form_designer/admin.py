from django.contrib import admin
from django.http import Http404
from django.urls import re_path, reverse
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from form_designer import settings
from form_designer.forms import FormDefinitionFieldInlineForm, FormDefinitionForm
from form_designer.models import FormDefinition, FormDefinitionField, FormLog


class FormDefinitionFieldInline(admin.StackedInline):
    form = FormDefinitionFieldInlineForm
    model = FormDefinitionField
    extra = 1
    fieldsets = [
        (_("Basic"), {"fields": ["name", "field_class", "required", "initial"]}),
        (
            _("Display"),
            {"fields": ["label", "widget", "help_text", "position", "include_result"]},
        ),
        (_("Text"), {"fields": ["max_length", "min_length"]}),
        (
            _("Numbers"),
            {"fields": ["max_value", "min_value", "max_digits", "decimal_places"]},
        ),
        (_("Regex"), {"fields": ["regex"]}),
        (_("Choices"), {"fields": ["choice_values", "choice_labels"]}),
        (_("Model Choices"), {"fields": ["choice_model", "choice_model_empty_label"]}),
    ]


class FormDefinitionAdmin(admin.ModelAdmin):
    save_as = True
    fieldsets = [
        (
            _("Basic"),
            {"fields": ["name", "require_hash", "method", "action", "title", "body"]},
        ),
        (
            _("Settings"),
            {
                "fields": [
                    "allow_get_initial",
                    "log_data",
                    "success_redirect",
                    "success_clear",
                    "display_logged",
                    "save_uploaded_files",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            _("Mail form"),
            {
                "fields": [
                    "mail_to",
                    "mail_from",
                    "mail_subject",
                    "mail_uploaded_files",
                    "mail_cover_text",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            _("Templates"),
            {
                "fields": ["message_template", "form_template_name"],
                "classes": ["collapse"],
            },
        ),
        (
            _("Messages"),
            {
                "fields": ["success_message", "error_message", "submit_label"],
                "classes": ["collapse"],
            },
        ),
    ]
    list_display = ("name", "title", "method", "count_fields")
    form = FormDefinitionForm
    inlines = [
        FormDefinitionFieldInline,
    ]
    search_fields = ("name", "title")


class FormLogAdmin(admin.ModelAdmin):
    list_display = ("form_definition", "created", "id", "created_by", "data_html")
    list_filter = ("form_definition",)
    list_display_links = None
    date_hierarchy = "created"

    exporter_classes = {}
    exporter_classes_ordered = []
    for class_path in settings.EXPORTER_CLASSES:
        cls = import_string(class_path)
        if cls.is_enabled():
            exporter_classes[cls.export_format()] = cls
            exporter_classes_ordered.append(cls)

    def get_exporter_classes(self):
        return self.__class__.exporter_classes_ordered

    def get_actions(self, request):
        actions = super().get_actions(request)

        for cls in self.get_exporter_classes():
            desc = (
                _("Export selected %%(verbose_name_plural)s as %s")
                % cls.export_format()
            )
            actions[cls.export_format()] = (cls.export_view, cls.export_format(), desc)

        return actions

    def get_urls(self):
        urls = [
            re_path(
                r"^export/(?P<format>[a-zA-Z0-9_-]+)/$",
                self.admin_site.admin_view(self.export_view),
                name="form_designer_export",
            ),
        ]
        return urls + super().get_urls()

    def data_html(self, obj):
        return obj.form_definition.compile_message(
            obj.data, "html/formdefinition/data_message.html"
        )

    data_html.allow_tags = True
    data_html.short_description = _("Data")

    def get_change_list_query_set(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        cl = self.get_changelist_instance(request)
        return cl.get_queryset(request)

    def export_view(self, request, format):
        queryset = self.get_change_list_query_set(request)
        if format not in self.exporter_classes:
            raise Http404()
        return self.exporter_classes[format](self.model).export(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        query_string = "?" + request.META.get("QUERY_STRING", "")
        exporter_links = []
        for cls in self.get_exporter_classes():
            url = (
                reverse("admin:form_designer_export", args=(cls.export_format(),))
                + query_string
            )
            exporter_links.append(
                {"url": url, "label": _("Export view as %s") % cls.export_format()}
            )

        extra_context["exporters"] = exporter_links

        return super().changelist_view(request, extra_context)


admin.site.register(FormDefinition, FormDefinitionAdmin)
admin.site.register(FormLog, FormLogAdmin)
