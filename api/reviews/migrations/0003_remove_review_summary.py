# Generated by Django 3.0 on 2022-03-31 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20220331_1858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='summary',
        ),
    ]