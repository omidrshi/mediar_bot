# Generated by Django 2.2.12 on 2020-07-23 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
