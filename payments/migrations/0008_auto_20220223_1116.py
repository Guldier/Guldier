# Generated by Django 3.2.12 on 2022-02-23 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20220223_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotiondaterange',
            name='promotion',
        ),
        migrations.AddField(
            model_name='promotion',
            name='dates',
            field=models.ManyToManyField(related_name='dates', to='payments.PromotionDateRange'),
        ),
    ]
