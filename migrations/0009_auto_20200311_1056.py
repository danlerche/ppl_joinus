# Generated by Django 2.2.9 on 2020-03-11 17:56

from django.db import migrations, models
import ppl_joinus.models


class Migration(migrations.Migration):

    dependencies = [
        ('ppl_joinus', '0008_auto_20200213_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joinusformfield',
            name='label',
            field=models.CharField(help_text='The label of the form field, cannot be one of the following: Your Name, Email, Your Phone Number.', max_length=255, validators=[ppl_joinus.models.validate_label], verbose_name='label'),
        ),
    ]
