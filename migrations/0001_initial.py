# Generated by Django 4.2.1 on 2023-10-24 18:37

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import ppl_joinus.models
import wagtail.contrib.forms.models
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0089_log_entry_data_json_null_to_object'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinusEvent',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.RichTextField(blank=True)),
                ('date', models.DateTimeField()),
                ('spots_available', models.PositiveIntegerField(default=0)),
                ('waitlist_spots_available', models.PositiveIntegerField(default=0)),
                ('success_email_msg', wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Body of the success email')),
                ('waitlist_email_msg', models.CharField(blank=True, max_length=2000, null=True, verbose_name='Body of the waitlist email')),
            ],
            options={
                'verbose_name': 'Joinus Event',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='JoinusFormPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('to_address', models.CharField(blank=True, help_text='Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.', max_length=255, validators=[wagtail.contrib.forms.models.validate_to_address], verbose_name='to address')),
                ('from_address', models.EmailField(blank=True, max_length=255, verbose_name='from address')),
                ('subject', models.CharField(blank=True, max_length=255, verbose_name='subject')),
            ],
            options={
                'verbose_name': 'Joinus Form Builder',
            },
            bases=(wagtail.contrib.forms.models.FormMixin, 'wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='JoinusUserFormBuilder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_data', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('submit_time', models.DateTimeField(auto_now_add=True, verbose_name='submit time')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.page')),
            ],
            options={
                'verbose_name': 'form submission',
                'verbose_name_plural': 'form submissions',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JoinusRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('wait_list', models.BooleanField(default=0)),
                ('event_name', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ppl_joinus.joinusevent')),
                ('user_info', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ppl_joinus.joinususerformbuilder')),
            ],
            options={
                'verbose_name': 'Event Registration',
            },
        ),
        migrations.CreateModel(
            name='JoinusFormField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('clean_name', models.CharField(blank=True, default='', help_text='Safe name of the form field, the label converted to ascii_snake_case', max_length=255, verbose_name='name')),
                ('field_type', models.CharField(choices=[('singleline', 'Single line text'), ('multiline', 'Multi-line text'), ('email', 'Email'), ('number', 'Number'), ('url', 'URL'), ('checkbox', 'Checkbox'), ('checkboxes', 'Checkboxes'), ('dropdown', 'Drop down'), ('multiselect', 'Multiple select'), ('radio', 'Radio buttons'), ('date', 'Date'), ('datetime', 'Date/time'), ('hidden', 'Hidden field')], max_length=16, verbose_name='field type')),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('choices', models.TextField(blank=True, help_text='Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.', verbose_name='choices')),
                ('default_value', models.TextField(blank=True, help_text='Default value. Comma or new line separated values supported for checkboxes.', verbose_name='default value')),
                ('help_text', models.CharField(blank=True, max_length=255, verbose_name='help text')),
                ('label', models.CharField(help_text='The label of the form field, cannot be one of the following: Your Name, Email.', max_length=255, validators=[ppl_joinus.models.validate_label], verbose_name='label')),
                ('form_builder_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_fields', to='ppl_joinus.joinusformpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='joinusevent',
            name='registration_form_chooser',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ppl_joinus.joinusformpage'),
        ),
    ]
