# Generated by Django 3.1.6 on 2021-04-07 11:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('preyes_app', '0017_passwordchangerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordchangerequest',
            name='requested_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 7, 11, 37, 36, 170889, tzinfo=utc)),
        ),
    ]
