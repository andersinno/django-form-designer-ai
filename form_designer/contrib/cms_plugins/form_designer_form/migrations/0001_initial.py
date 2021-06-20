import cms
from django.db import migrations, models
from pkg_resources import parse_version as V

# Django CMS 3.3.1 is oldest release where the change affects.
# Refs https://github.com/divio/django-cms/commit/871a164
if V(cms.__version__) >= V('3.3.1'):
    field_kwargs = {'related_name': 'form_designer_form_cmsformdefinition'}
else:
    field_kwargs = {}


class Migration(migrations.Migration):
    dependencies = [
        ('cms', '0001_initial'),
        ('form_designer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CMSFormDefinition',
            fields=[
                ('cmsplugin_ptr',
                 models.OneToOneField(
                     serialize=False,
                     auto_created=True,
                     primary_key=True,
                     to='cms.CMSPlugin',
                     parent_link=True,
                     on_delete=models.CASCADE,
                     **field_kwargs)),
                ('form_definition',
                 models.ForeignKey(
                     verbose_name='form',
                     to='form_designer.FormDefinition',
                     on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(
                'cms.cmsplugin',
            ),
        ),
    ]
