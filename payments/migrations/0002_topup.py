# Generated by Django 3.1.7 on 2021-11-29 21:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_intent_payment', models.IntegerField(default=0)),
                ('amount_from_stripe', models.IntegerField(null=True)),
                ('currency', models.CharField(default='pln', max_length=3)),
                ('date_intent_payment', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('payment_status', models.CharField(choices=[('new', 'new'), ('pending', 'pending'), ('success', 'success'), ('reject', 'reject')], default='new', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]