# Generated by Django 3.0 on 2022-03-17 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cvs', '0003_auto_20220317_0134'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cvexperience',
            old_name='job_status',
            new_name='job_state',
        ),
    ]