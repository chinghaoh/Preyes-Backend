# Generated by Django 3.1.6 on 2021-04-30 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preyes_app', '0028_auto_20210428_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='productitem',
            name='in_stock',
            field=models.BooleanField(default=True),
        ),
    ]