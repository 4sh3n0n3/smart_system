# Generated by Django 2.1.2 on 2018-12-25 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study_group_module', '0001_initial'),
        ('user_module', '0002_groups_and_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deaneryprofile',
            name='institute',
        ),
        migrations.AddField(
            model_name='deaneryprofile',
            name='institute',
            field=models.ManyToManyField(related_name='deanery_workers_profiles', to='study_group_module.Institute'),
        ),
    ]