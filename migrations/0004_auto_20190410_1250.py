# Generated by Django 2.1.7 on 2019-04-10 19:50

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ppl_joinus', '0003_successpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='joinusevent',
            name='success_page',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ppl_joinus.SuccessPage'),
        ),
        migrations.AlterField(
            model_name='successpage',
            name='body',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
