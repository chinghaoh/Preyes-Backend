# Generated by Django 3.1.6 on 2021-04-07 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preyes_app', '0018_auto_20210407_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordchangerequest',
            name='requested_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]