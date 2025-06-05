from django.db import migrations, models

import form_designer.fields


class Migration(migrations.Migration):
    dependencies = [
        ("form_designer", "0002_reply_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="formdefinition",
            name="mail_cover_text",
            field=models.TextField(
                help_text="Email cover text which can be included in the default email template and in the message template.",
                null=True,
                verbose_name="email cover text",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="formdefinition",
            name="message_template",
            field=form_designer.fields.TemplateTextField(
                help_text='Your form fields are available as template context. Example: "{{ message }}" if you have a field named `message`. To iterate over all fields, use the variable `data` (a list containing a dictionary for each form field, each containing the elements `name`, `label`, `value`). If you have set up email cover text, you can use {{ mail_cover_text }} to access it.',
                null=True,
                verbose_name="message template",
                blank=True,
            ),
        ),
    ]
