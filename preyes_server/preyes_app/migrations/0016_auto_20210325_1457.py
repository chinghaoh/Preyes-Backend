# Generated by Django 3.1.6 on 2021-03-25 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preyes_app', '0015_bol'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='auth_user_reference',
        ),
        migrations.AlterField(
            model_name='targetitem',
            name='target_price',
            field=models.DecimalField(decimal_places=2, max_digits=19),
        ),
    ]