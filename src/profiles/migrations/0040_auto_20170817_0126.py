# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-17 05:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0039_auto_20170817_0125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quranattendance',
            name='date',
        ),
        migrations.AlterField(
            model_name='quranattendance',
            name='week',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='profiles.SchoolWeeks'),
        ),
    ]