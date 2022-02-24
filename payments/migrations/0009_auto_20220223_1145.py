# Generated by Django 3.2.12 on 2022-02-23 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20220223_1116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='dates',
        ),
        migrations.AddField(
            model_name='promotion',
            name='dates',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dates', to='payments.promotiondaterange'),
        ),
    ]
