# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-29 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0055_profile_updated_google_sheets'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='activation_email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='islamicstudiesexam',
            name='class_level',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 'IS1'), (2, 'IS2'), (3, 'IS3'), (4, 'IS4'), (5, 'IS5'), (6, 'IS6'), (7, 'IS7'), (8, 'IS8'), (9, 'IS9'), (10, 'IS10')], null=True),
        ),
    ]
