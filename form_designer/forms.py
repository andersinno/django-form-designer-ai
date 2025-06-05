import os

from django import forms
from django.conf import settings as django_settings
from django.forms import widgets
from django.forms.widgets import Select
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from form_designer import settings
from form_designer.models import FormDefinition, FormDefinitionField
from form_designer.uploads import clean_files


class DesignedForm(forms.Form):
    def __init__(self, form_definition, initial_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_fields = []
        for def_field in form_definition.formdefinitionfield_set.all():
            self.add_defined_field(def_field, initial_data)
        self.fields[form_definition.submit_flag_name] = forms.BooleanField(
            required=False, initial=1, widget=widgets.HiddenInput
        )

    def add_defined_field(self, def_field, initial_data=None):
        if initial_data and def_field.name in initial_data:
            if def_field.field_class not in (
                "django.forms.MultipleChoiceField",
                "django.forms.ModelMultipleChoiceField",
            ):
                def_field.initial = initial_data.get(def_field.name)
            else:
                def_field.initial = initial_data.getlist(def_field.name)
        field = import_string(def_field.field_class)(
            **def_field.get_form_field_init_args()
        )
        self.fields[def_field.name] = field
        if isinstance(field, forms.FileField):
            self.file_fields.append(def_field)

    def clean(self):
        return clean_files(self)


class FormDefinitionFieldInlineForm(forms.ModelForm):
    class Meta:
        model = FormDefinitionField
        exclude = ()

    def clean_regex(self):
        if (
            not self.cleaned_data["regex"]
            and "field_class" in self.cleaned_data
            and self.cleaned_data["field_class"] in ("django.forms.RegexField",)
        ):
            raise forms.ValidationError(
                _("This field class requires a regular expression.")
            )
        return self.cleaned_data["regex"]

    def clean_choice_model(self):
        if (
            not self.cleaned_data["choice_model"]
            and "field_class" in self.cleaned_data
            and self.cleaned_data["field_class"]
            in (
                "django.forms.ModelChoiceField",
                "django.forms.ModelMultipleChoiceField",
            )
        ):
            raise forms.ValidationError(_("This field class requires a model."))
        return self.cleaned_data["choice_model"]

    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)
        for field_name, choices in (
            ("field_class", settings.FIELD_CLASSES),
            ("widget", settings.WIDGET_CLASSES),
            ("choice_model", settings.CHOICE_MODEL_CHOICES),
        ):
            if choices is None:
                continue
            if field_name in self.fields:
                self.fields[field_name].widget = Select(choices=choices)
                if not self.initial.get(field_name):
                    self.initial[field_name] = choices[0][0]


class FormDefinitionForm(forms.ModelForm):
    class Meta:
        model = FormDefinition
        exclude = ()

    def _media(self):
        js = []
        plugins = [
            "js/jquery-ui.js",
            "js/jquery-inline-positioning.js",
            "js/jquery-inline-rename.js",
            "js/jquery-inline-collapsible.js",
            "js/jquery-inline-fieldset-collapsible.js",
            "js/jquery-inline-prepopulate-label.js",
        ]
        if hasattr(django_settings, "JQUERY_URL"):
            js.append(django_settings.JQUERY_URL)
        else:
            plugins = ["js/jquery.js"] + plugins
        js.extend([os.path.join(settings.STATIC_URL, path) for path in plugins])
        return forms.Media(js=js)

    media = property(_media)

    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)
        if "form_template_name" in self.fields:
            self.fields["form_template_name"].widget = Select(
                choices=settings.FORM_TEMPLATES
            )
