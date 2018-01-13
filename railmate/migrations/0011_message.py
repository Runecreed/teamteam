# Generated by Django 2.0.1 on 2018-01-13 20:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('railmate', '0010_auto_20180112_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='', verbose_name='Content')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='sent at')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='read at')),
                ('recipient', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='received_dm', to=settings.AUTH_USER_MODEL, verbose_name='Recipient')),
                ('sender', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sent_dm', to=settings.AUTH_USER_MODEL, verbose_name='Sender')),
            ],
        ),
    ]
