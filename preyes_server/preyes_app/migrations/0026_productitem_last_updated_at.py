# Generated by Django 3.1.6 on 2021-04-28 12:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preyes_app', '0025_auto_20210421_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='productitem',
            name='last_updated_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]