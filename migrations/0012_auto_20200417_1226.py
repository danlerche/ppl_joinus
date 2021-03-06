# Generated by Django 2.2.9 on 2020-04-17 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ppl_joinus', '0011_auto_20200417_1056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='joinusevent',
            old_name='success_message',
            new_name='success_email_msg',
        ),
        migrations.AddField(
            model_name='joinusevent',
            name='success_email_sub',
            field=models.CharField(default='You have succesfully registered for <django.db.models.fields.PositiveIntegerField>', max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='joinusevent',
            name='waitlist_email_msg',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='joinusevent',
            name='waitlist_email_sub',
            field=models.CharField(max_length=2000, null=True),
        ),
    ]
