# Generated by Django 3.0 on 2022-03-22 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        ('employers', '0002_auto_20220322_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='employer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employer_job', to='employers.Employer'),
        ),
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_type_job', to='jobs.JobType'),
        ),
        migrations.AddField(
            model_name='job',
            name='tag',
            field=models.ManyToManyField(db_table='jobs_tags', related_name='jobs_tags', to='jobs.Tag'),
        ),
    ]
