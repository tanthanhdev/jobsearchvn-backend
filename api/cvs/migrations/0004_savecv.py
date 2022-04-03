# Generated by Django 3.0 on 2022-04-03 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employers', '0002_auto_20220322_1224'),
        ('cvs', '0003_auto_20220322_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaveCv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_save_cvs', to='cvs.Cv')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employer_save_cvs', to='employers.Employer')),
            ],
            options={
                'db_table': 'save_cvs',
                'ordering': ('-pk',),
            },
        ),
    ]
