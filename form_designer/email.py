import re

from django.core.mail import EmailMessage
from django.utils.encoding import force_str

from form_designer.utils import string_template_replace


def _template_replace_list(input_str, context_dict):
    """
    Split the input string by commas or semicolons, then template-replace.

    Falsy input values yield empty lists.

    :param input_str: Comma-or-semicolon-separated list of values
    :type input_str: str|None
    :param context_dict: The context for template replacement
    :return: List of strings
    :rtype: list[str]
    """
    if not input_str:
        return []
    return [
        string_template_replace(email, context_dict)
        for email in re.compile(r"\s*[,;]+\s*").split(force_str(input_str))
    ]


def build_form_mail(form_definition, form, files=None):
    """
    Build a form-submission email based on the given form definition and associated submitted form

    :param form_definition: Form definition object
    :param form: The freshly submitted form
    :param files: Associated files
    :return: Django email message
    """
    if not files:
        files = []
    form_data = form_definition.get_form_data(form)
    message = form_definition.compile_message(form_data)
    context_dict = form_definition.get_form_data_context(form_data)

    mail_to = _template_replace_list(form_definition.mail_to, context_dict)

    if form_definition.mail_from:
        from_email = string_template_replace(form_definition.mail_from, context_dict)
    else:
        from_email = None

    reply_to = _template_replace_list(form_definition.mail_reply_to, context_dict)

    mail_subject = string_template_replace(
        (form_definition.mail_subject or form_definition.title), context_dict
    )

    kwargs = {
        "subject": mail_subject,
        "body": message,
        "from_email": from_email,
        "to": mail_to,
        "reply_to": reply_to,
    }

    message = EmailMessage(**kwargs)

    if form_definition.is_template_html:
        message.content_subtype = "html"

    if form_definition.mail_uploaded_files:
        for file_path in files:
            message.attach_file(file_path)

    return message
