from django import forms
from django.apps import apps
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ModelNameFormField(forms.CharField):
    @staticmethod
    def get_model_from_string(model_path):
        try:
            app_label, model_name = model_path.rsplit(".models.")
            return apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            return None

    def clean(self, value):
        """
        Validates that the input matches the regular expression. Returns a
        string object.
        """
        value = super().clean(value)
        if value in validators.EMPTY_VALUES:
            return ""
        if not ModelNameFormField.get_model_from_string(value):
            raise ValidationError(
                _(
                    "Model could not be imported: %(value)s. Please use a valid model path."
                ),
                code="invalid",
                params={"value": value},
            )
        return value


class ModelNameField(models.CharField):
    @staticmethod
    def get_model_from_string(model_path):
        return ModelNameFormField.get_model_from_string(model_path)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": ModelNameFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class TemplateFormField(forms.CharField):
    def clean(self, value):
        """
        Validates that the input can be compiled as a template.
        """
        value = super().clean(value)
        from django.template import Template, TemplateSyntaxError

        if value:
            try:
                Template(value)
            except TemplateSyntaxError as error:
                raise ValidationError(error)
        return value


class TemplateCharField(models.CharField):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": TemplateFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class TemplateTextField(models.TextField):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": TemplateFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class RegexpExpressionFormField(forms.CharField):
    def clean(self, value):
        """
        Validates that the input can be compiled as a Regular Expression.
        """
        value = super().clean(value)
        if value in validators.EMPTY_VALUES:
            value = ""
        import re

        try:
            re.compile(value)
        except Exception as error:
            raise ValidationError(error)
        return value


class RegexpExpressionField(models.CharField):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": RegexpExpressionFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
