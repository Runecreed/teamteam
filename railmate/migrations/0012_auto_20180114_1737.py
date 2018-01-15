# Generated by Django 2.0.1 on 2018-01-14 16:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('railmate', '0011_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='date',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='time',
        ),
        migrations.AddField(
            model_name='trip',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trip',
            name='datetime_end',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trip',
            name='tripnumber',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]