# Generated by Django 3.0.3 on 2020-03-19 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_orders'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orders',
            options={'verbose_name_plural': 'Orders'},
        ),
        migrations.AddField(
            model_name='orders',
            name='landmark',
            field=models.CharField(default='', max_length=100),
        ),
    ]
