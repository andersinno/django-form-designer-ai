import json
from urllib.request import Request, urlopen

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.utils.http import urlencode
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from form_designer import settings as app_settings
from form_designer.models import FormDefinition
from form_designer.signals import (
    designedform_error,
    designedform_render,
    designedform_submit,
    designedform_success,
)
from form_designer.uploads import handle_uploaded_files


def get_designed_form_class():
    return import_string(app_settings.DESIGNED_FORM_CLASS)


def check_recaptcha(request, context, push_messages):
    is_valid = True
    if not app_settings.USE_GOOGLE_RECAPTCHA:
        return is_valid
    """ Begin reCAPTCHA validation """
    recaptcha_response = request.POST.get("g-recaptcha-response")
    url = "https://www.google.com/recaptcha/api/siteverify"
    values = {
        "secret": app_settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        "response": recaptcha_response,
    }
    data = urlencode(values).encode("utf-8")
    req = Request(url, data)
    response = urlopen(req)
    result = json.load(response)
    """ End reCAPTCHA validation """
    if not result["success"]:
        is_valid = False
        error_message = _("Invalid reCAPTCHA.")
        if push_messages:
            messages.error(request, error_message)
    return is_valid


def update_recaptcha_context(context):
    if not app_settings.USE_GOOGLE_RECAPTCHA:
        return
    context.update(
        {
            "use_google_recaptcha": True,
            "google_recaptcha_site_key": app_settings.GOOGLE_RECAPTCHA_SITE_KEY,
        }
    )


def process_form(  # noqa: C901
    request,
    form_definition,
    extra_context=None,
    disable_redirection=False,
    push_messages=True,
    form_class=None,
):
    if extra_context is None:
        extra_context = {}
    if form_class is None:
        form_class = get_designed_form_class()
    context = extra_context
    success_message = form_definition.success_message or _(
        "Thank you, the data was submitted successfully."
    )
    error_message = form_definition.error_message or _(
        "The data could not be submitted, please try again."
    )
    form_error = False
    form_success = False
    is_submit = False
    # If the form has been submitted...
    if request.method == "POST" and request.POST.get(form_definition.submit_flag_name):
        form = form_class(form_definition, None, request.POST, request.FILES)
        is_submit = True
    if request.method == "GET" and request.GET.get(form_definition.submit_flag_name):
        form = form_class(form_definition, None, request.GET)
        is_submit = True

    if is_submit:
        designedform_submit.send(
            sender=process_form,
            context=context,
            form_definition=form_definition,
            request=request,
        )
        recaptcha_is_valid = check_recaptcha(request, context, push_messages)
        if form.is_valid() and recaptcha_is_valid:
            # Handle file uploads using storage object
            files = handle_uploaded_files(form_definition, form)

            # Successful submission
            if push_messages:
                messages.success(request, success_message)
            form_success = True

            designedform_success.send(
                sender=process_form,
                context=context,
                form_definition=form_definition,
                request=request,
            )

            if form_definition.log_data:
                context["form_log"] = form_definition.log(form, request.user)
            if form_definition.mail_to:
                context["form_mail_message"] = form_definition.send_mail(form, files)
            if form_definition.success_redirect and not disable_redirection:
                return HttpResponseRedirect(form_definition.action or "?")
            if form_definition.success_clear:
                form = form_class(form_definition)  # clear form
        else:
            form_error = True
            designedform_error.send(
                sender=process_form,
                context=context,
                form_definition=form_definition,
                request=request,
            )
            if push_messages:
                messages.error(request, error_message)
    else:
        if form_definition.allow_get_initial:
            form = form_class(form_definition, initial_data=request.GET)
        else:
            form = form_class(form_definition)
        designedform_render.send(
            sender=process_form,
            context=context,
            form_definition=form_definition,
            request=request,
        )

    context.update(
        {
            "form_error": form_error,
            "form_success": form_success,
            "form_success_message": success_message,
            "form_error_message": error_message,
            "form": form,
            "form_definition": form_definition,
        }
    )
    context.update(csrf(request))
    update_recaptcha_context(context)

    if form_definition.display_logged:
        logs = form_definition.logs.all().order_by("created")
        context.update({"logs": logs})

    return context


def _form_detail_view(request, form_definition):
    result = process_form(request, form_definition)
    if isinstance(result, HttpResponseRedirect):
        return result
    result.update(
        {
            "form_template": form_definition.form_template_name
            or app_settings.DEFAULT_FORM_TEMPLATE
        }
    )
    return render("html/formdefinition/detail.html", result)


def detail(request, object_name):
    form_definition = get_object_or_404(
        FormDefinition, name=object_name, require_hash=False
    )
    return _form_detail_view(request, form_definition)


def detail_by_hash(request, public_hash):
    form_definition = get_object_or_404(FormDefinition, public_hash=public_hash)
    return _form_detail_view(request, form_definition)
