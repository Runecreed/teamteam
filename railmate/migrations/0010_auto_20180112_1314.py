# Generated by Django 2.0 on 2018-01-12 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railmate', '0009_auto_20180112_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatar'),
        ),
    ]