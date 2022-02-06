# Generated by Django 3.1.6 on 2022-02-06 11:36

import django.core.validators
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_remove_topup_customer_email'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='topup',
            managers=[
                ('payments', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='topup',
            name='amount',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(15)]),
        ),
    ]
