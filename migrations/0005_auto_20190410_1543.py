# Generated by Django 2.1.7 on 2019-04-10 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ppl_joinus', '0004_auto_20190410_1250'),
    ]

    operations = [
        migrations.RenameField(
            model_name='joinusevent',
            old_name='form_chooser',
            new_name='registration_form_chooser',
        ),
    ]
