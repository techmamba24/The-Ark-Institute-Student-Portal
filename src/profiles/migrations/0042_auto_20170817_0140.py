# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-17 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0041_auto_20170817_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quranattendance',
            name='class_level',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4'), (5, 'Q5'), (6, 'Q6'), (7, 'Q7'), (8, 'Q8'), (9, 'Q9')], null=True),
        ),
    ]