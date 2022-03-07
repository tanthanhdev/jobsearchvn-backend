# Generated by Django 3.0 on 2022-03-06 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employers', '0002_auto_20220306_2242'),
        ('jobs', '0002_auto_20220306_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_job', to='jobs.Country'),
        ),
        migrations.AlterField(
            model_name='job',
            name='employer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employer_job', to='employers.Employer'),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_type_job', to='jobs.JobType'),
        ),
    ]
