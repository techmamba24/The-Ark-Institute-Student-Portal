# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-06 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20170806_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Student'), (2, 'Teacher'), (3, 'Admin')], null=True),
        ),
    ]
