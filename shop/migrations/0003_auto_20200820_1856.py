# Generated by Django 3.1 on 2020-08-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_chart'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('addon_type', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='chart',
            name='dish',
        ),
        migrations.RemoveField(
            model_name='orders',
            name='dish',
        ),
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.addon')),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.dish')),
            ],
        ),
        migrations.AddField(
            model_name='chart',
            name='composition',
            field=models.ForeignKey( on_delete=django.db.models.deletion.CASCADE, to='shop.composition'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orders',
            name='composition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.composition'),
            preserve_default=False,
        ),
    ]
