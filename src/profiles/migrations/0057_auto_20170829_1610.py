# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-29 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0056_auto_20170829_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='islamicstudiesattendance',
            name='class_level',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'IS1'), (2, 'IS2'), (3, 'IS3'), (4, 'IS4'), (5, 'IS5'), (6, 'IS6'), (7, 'IS7'), (8, 'IS8'), (9, 'IS9'), (10, 'IS10')], null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='islamic_studies_class',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'IS1'), (2, 'IS2'), (3, 'IS3'), (4, 'IS4'), (5, 'IS5'), (6, 'IS6'), (7, 'IS7'), (8, 'IS8'), (9, 'IS9'), (10, 'IS10')], null=True),
        ),
    ]
