# Generated by Django 5.2.3 on 2025-08-01 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_alter_candidate_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='require_dues_payment',
            field=models.BooleanField(default=False),
        ),
    ]
