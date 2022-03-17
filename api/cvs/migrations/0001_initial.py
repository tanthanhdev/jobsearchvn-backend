# Generated by Django 3.0 on 2022-03-16 23:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
                ('view', models.BigIntegerField(blank=True, default=0)),
                ('target_major', models.TextField()),
                ('status', models.CharField(blank=True, default=1, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'cvs',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='Cv_Career',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'cv_careers',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='Cv_Design',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'cv_designs',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='CvSocialActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('unit_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('starting_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_cv_social_activities', to='cvs.Cv')),
            ],
            options={
                'db_table': 'cv_social_activities',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='CvSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_cv_skills', to='cvs.Cv')),
            ],
            options={
                'db_table': 'cv_skills',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='CvExperience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=255)),
                ('company_name', models.CharField(max_length=255)),
                ('job_location', models.CharField(blank=True, max_length=255, null=True)),
                ('job_state', models.CharField(max_length=255)),
                ('job_country', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_cv_experiences', to='cvs.Cv')),
            ],
            options={
                'db_table': 'cv_experiences',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='CvEducation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree_name', models.CharField(max_length=255)),
                ('major', models.CharField(max_length=255)),
                ('university_name', models.CharField(max_length=255)),
                ('gpa', models.FloatField()),
                ('starting_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_cv_educations', to='cvs.Cv')),
            ],
            options={
                'db_table': 'cv_educations',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='CvCertificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('year', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_cv_certificaties', to='cvs.Cv')),
            ],
            options={
                'db_table': 'cv_certificaties',
                'ordering': ('-pk',),
            },
        ),
        migrations.AddField(
            model_name='cv',
            name='cv_career',
            field=models.ManyToManyField(db_table='cvs_cv_carrers', related_name='cvs_cv_carrers', to='cvs.Cv_Career'),
        ),
        migrations.AddField(
            model_name='cv',
            name='cv_design',
            field=models.ManyToManyField(db_table='cvs_cv_designs', related_name='cvs_cv_designs', to='cvs.Cv_Design'),
        ),
        migrations.AddField(
            model_name='cv',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_cvs', to=settings.AUTH_USER_MODEL),
        ),
    ]
